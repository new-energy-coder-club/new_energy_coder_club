#!/usr/bin/env node

/**
 * IMAP Email CLI
 * Works with any standard IMAP server (Gmail, ProtonMail Bridge, Fastmail, etc.)
 * Supports IMAP ID extension (RFC 2971) for 163.com and other servers
 */

const Imap = require('imap');
const { simpleParser } = require('mailparser');
const path = require('path');
const fs = require('fs');
const os = require('os');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

// ──────────────────────────────────────────────────────────────
// Monkey-patch: 修补 node-imap Parser 的 LIST/LSUB 解析
//
// 搜狐 (imap.sohu.com) 等邮箱服务器返回偏离 RFC-3501 标准的
// LIST/LSUB 未标记响应，node-imap 的 parseBoxList 调用 parseExpr
// 时会 throw，导致 Node 进程崩溃。
//
// 此 patch 在 Parser.prototype._resUntagged 中为 LIST/LSUB/XLIST
// 的解析加上 try-catch，遇到解析失败时静默跳过该行而不是崩溃。
// ──────────────────────────────────────────────────────────────
(function patchImapParser() {
  try {
    const parserModule = require('imap/lib/Parser');
    const ParserClass = parserModule.Parser;
    if (!ParserClass || !ParserClass.prototype._resUntagged) return;

    const origResUntagged = ParserClass.prototype._resUntagged;

    ParserClass.prototype._resUntagged = function patchedResUntagged() {
      try {
        return origResUntagged.call(this);
      } catch (parseErr) {
        // 解析失败 → 清空 buffer，静默跳过这行非标准响应
        this._buffer = '';
        this._literals = [];
        if (process.env.DEBUG_EMAIL_SKILL === 'true') {
          process.stderr.write(
            `[imap-patch] Skipped non-standard untagged response: ${String(parseErr.message || parseErr).slice(0, 200)}\n`
          );
        }
        // 不 throw，不 emit error → 连接继续工作
      }
    };
  } catch (e) {
    // node-imap 内部结构变化时退化：patch 失败不影响正常功能
  }
})();

// 全局捕获 node-imap 内部其他位置可能抛出的未处理异常（最后兜底）
process.on('uncaughtException', (err) => {
  const msg = String(err && err.message ? err.message : err || '');
  console.log(JSON.stringify({
    success: false,
    error_code: 1,
    message: `未预期的异常：${msg}`,
  }, null, 2));
  process.exit(1);
});

process.on('unhandledRejection', (err) => {
  const msg = String(err && err.message ? err.message : err || '');
  console.log(JSON.stringify({
    success: false,
    error_code: 1,
    message: `未处理的 Promise 异常：${msg}`,
  }, null, 2));
  process.exit(1);
});

const DEFAULT_MAILBOX = process.env.IMAP_MAILBOX || 'INBOX';
const NETEASE_DOMAINS = ['163.com', 'vip.163.com', '126.com', 'vip.126.com', '188.com', 'vip.188.com', 'yeah.net'];
const SOHU_DOMAINS = ['sohu.com'];
const CERTIFICATE_ERROR_CODES = new Set([
  'DEPTH_ZERO_SELF_SIGNED_CERT',
  'SELF_SIGNED_CERT_IN_CHAIN',
  'UNABLE_TO_VERIFY_LEAF_SIGNATURE',
  'ERR_TLS_CERT_ALTNAME_INVALID',
  'CERT_HAS_EXPIRED',
  'UNABLE_TO_GET_ISSUER_CERT_LOCALLY',
]);
const RETRYABLE_NETWORK_CODES = new Set([
  'ECONNRESET',
  'ETIMEDOUT',
  'ESOCKET',
  'ECONNABORTED',
  'EPIPE',
  'EAI_AGAIN',
  'ENOTFOUND',
  'ECONNREFUSED',
  'EHOSTUNREACH',
  'ENETUNREACH',
]);

function validateWritePath(dirPath) {
  const allowedDirsStr = process.env.ALLOWED_WRITE_DIRS;
  if (!allowedDirsStr) {
    throw new Error('ALLOWED_WRITE_DIRS not set in .env. Attachment download is disabled.');
  }

  const resolved = path.resolve(dirPath.replace(/^~/, os.homedir()));

  const allowedDirs = allowedDirsStr.split(',').map((d) =>
    path.resolve(d.trim().replace(/^~/, os.homedir()))
  );

  const allowed = allowedDirs.some((dir) =>
    resolved === dir || resolved.startsWith(dir + path.sep)
  );

  if (!allowed) {
    throw new Error(`Access denied: '${dirPath}' is outside allowed write directories`);
  }

  return resolved;
}

function sanitizeFilename(filename) {
  return path.basename(filename).replace(/\.\./g, '').replace(/^[./\\]/, '') || 'attachment';
}

// IMAP ID information for 163.com compatibility
const IMAP_ID = {
  name: 'openclaw',
  version: '0.0.1',
  vendor: 'netease',
  'support-email': 'kefu@188.com',
};

// Parse command-line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const command = args[0];
  const options = {};
  const positional = [];

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith('--')) {
        options[key] = next;
        i++;
      } else {
        options[key] = true;
      }
    } else {
      positional.push(arg);
    }
  }

  return { command, options, positional };
}

function isTruthyOption(value) {
  if (value === true) {
    return true;
  }
  const normalized = String(value || '').trim().toLowerCase();
  return ['1', 'true', 'yes', 'y', 'on'].includes(normalized);
}

function parseBooleanEnv(name, defaultValue) {
  if (process.env[name] === undefined) {
    return defaultValue;
  }
  return isTruthyOption(process.env[name]);
}

function parseNumberEnv(name, defaultValue) {
  const raw = String(process.env[name] || '').trim();
  if (!raw) {
    return defaultValue;
  }
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : defaultValue;
}

function isIpLiteral(host) {
  return /^\d{1,3}(\.\d{1,3}){3}$/.test(host) || host.includes(':');
}

function getConfiguredIdentity() {
  return String(
    process.env.EMAIL_PROVIDER_HINT
      || process.env.IMAP_HOST
      || process.env.SMTP_HOST
      || process.env.IMAP_USER
      || process.env.SMTP_USER
      || ''
  ).trim().toLowerCase();
}

function isNeteaseProvider() {
  const identity = getConfiguredIdentity();
  return NETEASE_DOMAINS.some((domain) =>
    identity === domain || identity.endsWith(`.${domain}`) || identity.endsWith(`@${domain}`) || identity.includes(domain)
  );
}

function isSohuProvider() {
  const identity = getConfiguredIdentity();
  return SOHU_DOMAINS.some((domain) =>
    identity === domain || identity.endsWith(`.${domain}`) || identity.endsWith(`@${domain}`) || identity.includes(domain)
  );
}

function getProviderAwareDefault(neteaseValue, standardValue) {
  // 搜狐邮箱与网易一样需要更宽松的超时参数（服务器响应慢、协议不完全标准）
  return (isNeteaseProvider() || isSohuProvider()) ? neteaseValue : standardValue;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function normalizeErrorMessage(err) {
  return String(err && err.message ? err.message : err || '')
    .replace(/^Error:\s*/i, '')
    .trim();
}

function containsAny(text, patterns) {
  const normalized = String(text || '').toLowerCase();
  return patterns.some((pattern) => normalized.includes(String(pattern).toLowerCase()));
}

function isCertificateError(err) {
  const code = String(err && err.code ? err.code : '').toUpperCase();
  const message = normalizeErrorMessage(err);
  return CERTIFICATE_ERROR_CODES.has(code) || containsAny(message, [
    'certificate',
    'self signed',
    'unable to verify',
    'hostname/ip does not match certificate',
    'altname',
    'ssl routines',
  ]);
}

function isAuthError(err) {
  const message = normalizeErrorMessage(err);
  return containsAny(message, [
    'auth',
    'authenticationfailed',
    'authentication failed',
    'invalid login',
    'login failed',
    '535',
    'bad credentials',
    'web login required',
  ]);
}

/**
 * 检测网易系邮箱"不安全登录"风控拦截错误。
 * 与 isAuthError（密码/授权码错误）不同，这种错误通常是风控系统拒绝连接，
 * 常见原因：未声明 IMAP ID 客户端身份、代理/VPN、频繁重试等。
 */
function isUnsafeLoginError(err) {
  const message = normalizeErrorMessage(err);
  return containsAny(message, [
    'unsafe login',
    'unsafe',
    'login denied',
  ]);
}

function isRetryableConnectionError(err) {
  if (!err || isCertificateError(err) || isAuthError(err)) {
    return false;
  }

  const code = String(err.code || '').toUpperCase();
  const message = normalizeErrorMessage(err);
  return RETRYABLE_NETWORK_CODES.has(code) || containsAny(message, [
    'timed out',
    'timeout',
    'socket closed',
    'connection ended unexpectedly',
    'client network socket disconnected',
    'read econnreset',
    'greeting never received',
    'unable to reach',
  ]);
}

function buildTlsOptions(prefix, host) {
  const tlsOptions = {
    rejectUnauthorized: parseBooleanEnv(`${prefix}_REJECT_UNAUTHORIZED`, true),
  };

  const explicitServername = String(process.env[`${prefix}_SERVERNAME`] || '').trim();
  const servername = explicitServername || host;
  if (servername && !isIpLiteral(servername)) {
    tlsOptions.servername = servername;
  }

  const minVersion = String(process.env[`${prefix}_TLS_MIN_VERSION`] || '').trim();
  if (minVersion) {
    tlsOptions.minVersion = minVersion;
  }

  return tlsOptions;
}

function buildConnectionError(err, protocol, host, attempts) {
  const message = normalizeErrorMessage(err);
  const hostLabel = host || '未配置主机';
  const attemptNote = attempts > 1 ? ` 已自动重试 ${attempts} 次。` : '';

  if (isCertificateError(err)) {
    return new Error(
      `${protocol} SSL 证书校验失败（${hostLabel}）。如果你连接的是官方邮箱域名，这通常表示本机代理/安全软件替换了证书，或系统时间/根证书异常；如果你连接的是自建网关，可将 ${protocol}_REJECT_UNAUTHORIZED=false 后重试。原始错误：${message}`
    );
  }

  if (protocol === 'IMAP' && isNeteaseProvider() && isUnsafeLoginError(err)) {
    return new Error(
      `${protocol} 被网易服务器判定为不安全登录（${hostLabel}）。这通常不是端口号问题；网易官方说明更常见的根因是客户端未正确声明 IMAP ID 身份信息，或当前登录被风控。当前脚本已尝试发送 IMAP ID，如仍出现该错误，请优先检查：1）网页端已开启 IMAP；2）使用客户端授权码而不是网页登录密码；3）避免代理/VPN/频繁重试；4）先在网页端完成一次安全验证后再重试。原始错误：${message}`
    );
  }

  if (isNeteaseProvider() && isAuthError(err)) {
    return new Error(
      `${protocol} 登录失败（${hostLabel}）。网易系邮箱通常需要先在网页端开启 IMAP/SMTP，并使用客户端授权码而不是网页登录密码。原始错误：${message}`
    );
  }

  if (isSohuProvider() && isAuthError(err)) {
    return new Error(
      `${protocol} 登录失败（${hostLabel}）。搜狐邮箱需要先在网页端（mail.sohu.com）的「设置 → 客户端设置」中开启 IMAP/SMTP 服务，` +
      `并使用独立密码（客户端授权码）而不是网页登录密码。原始错误：${message}`
    );
  }

  if (isSohuProvider() && containsAny(message, ['unexpected', 'parse', 'bad server', 'invalid'])) {
    return new Error(
      `${protocol} 连接搜狐邮箱时遇到协议兼容问题（${hostLabel}）。搜狐 IMAP 服务器返回了不完全符合 RFC-3501 标准的响应，` +
      `当前已启用协议兼容补丁。如果问题持续，可能是搜狐服务端临时异常，请稍后重试。${attemptNote}原始错误：${message}`
    );
  }

  if (isRetryableConnectionError(err)) {
    return new Error(
      `${protocol} 连接不稳定（${hostLabel}）：${message}。这类错误常见于邮箱服务端短时抖动、限流或本地网络波动。${attemptNote}`.trim()
    );
  }

  return new Error(`${protocol} 连接失败（${hostLabel}）：${message || '未知错误'}`);
}

function formatImapCliError(err) {
  const message = normalizeErrorMessage(err);
  if (
    message.startsWith('Missing IMAP_')
    || message.startsWith('UID required:')
    || message.startsWith('Invalid time format.')
    || message.startsWith('Access denied:')
    || message.includes('not found')
  ) {
    return message;
  }
  return buildConnectionError(err, 'IMAP', process.env.IMAP_HOST, 1).message;
}

function resolveImapTlsEnabled(port) {
  if (process.env.IMAP_TLS === undefined) {
    return port === 993;
  }
  return parseBooleanEnv('IMAP_TLS', true);
}

// Create IMAP connection config
function createImapConfig() {
  const host = String(process.env.IMAP_HOST || '').trim();
  if (!host) {
    throw new Error('Missing IMAP_HOST environment variable');
  }

  const port = parseNumberEnv('IMAP_PORT', 993);
  const tls = resolveImapTlsEnabled(port);
  const config = {
    user: process.env.IMAP_USER,
    password: process.env.IMAP_PASS,
    host,
    port,
    tls,
    tlsOptions: buildTlsOptions('IMAP', host),
    connTimeout: parseNumberEnv('IMAP_CONN_TIMEOUT_MS', getProviderAwareDefault(20000, 10000)),
    authTimeout: parseNumberEnv('IMAP_AUTH_TIMEOUT_MS', getProviderAwareDefault(15000, 8000)),
    socketTimeout: parseNumberEnv('IMAP_SOCKET_TIMEOUT_MS', getProviderAwareDefault(30000, 20000)),
    keepalive: {
      interval: parseNumberEnv('IMAP_KEEPALIVE_INTERVAL_MS', 10000),
      idleInterval: parseNumberEnv('IMAP_IDLE_INTERVAL_MS', 300000),
      forceNoop: parseBooleanEnv('IMAP_FORCE_NOOP_KEEPALIVE', false),
    },
  };

  const autotls = String(process.env.IMAP_AUTOTLS || '').trim();
  if (autotls) {
    config.autotls = autotls;
  }

  return config;
}

function connectOnce(config) {
  return new Promise((resolve, reject) => {
    const imap = new Imap(config);
    let settled = false;

    const cleanup = () => {
      imap.removeListener('ready', onReady);
      imap.removeListener('error', onError);
      imap.removeListener('end', onEnd);
      imap.removeListener('close', onClose);
    };

    const rejectOnce = (err) => {
      if (settled) {
        return;
      }
      settled = true;
      cleanup();
      try {
        imap.destroy();
      } catch (destroyError) {
        // ignore destroy errors
      }
      reject(err);
    };

    const resolveOnce = () => {
      if (settled) {
        return;
      }
      settled = true;
      cleanup();
      // 捕获运行时错误（包括非标准 LIST/LSUB 响应解析失败），防止进程崩溃
      imap.on('error', (runtimeError) => {
        const msg = normalizeErrorMessage(runtimeError);
        if (process.env.DEBUG_EMAIL_SKILL === 'true') {
          process.stderr.write(`[imap runtime error] ${msg}\n`);
        }
        // 某些邮箱服务器（如搜狐）返回非标准 LIST/LSUB 响应，
        // node-imap 解析失败会触发 error 事件，这里静默吞掉以免崩溃
      });
      resolve(imap);
    };

    const onReady = () => {
      if (typeof imap.id === 'function') {
        imap.id(IMAP_ID, (idError) => {
          if (idError && isNeteaseProvider()) {
            rejectOnce(new Error(`IMAP ID command failed: ${normalizeErrorMessage(idError)}`));
            return;
          }
          resolveOnce();
        });
        return;
      }

      if (isNeteaseProvider()) {
        rejectOnce(new Error('Current IMAP client does not expose IMAP ID support, but Netease IMAP requires client identity information to avoid Unsafe Login'));
        return;
      }

      resolveOnce();
    };

    const onError = (err) => rejectOnce(err);
    const onEnd = () => rejectOnce(new Error('IMAP socket ended before connection became ready'));
    const onClose = () => rejectOnce(new Error('IMAP socket closed before connection became ready'));

    imap.once('ready', onReady);
    imap.once('error', onError);
    imap.once('end', onEnd);
    imap.once('close', onClose);
    imap.connect();
  });
}

// Connect to IMAP server with ID support
async function connect() {
  const config = createImapConfig();

  if (!config.user || !config.password) {
    throw new Error('Missing IMAP_USER or IMAP_PASS environment variables');
  }

  const attempts = Math.max(1, parseNumberEnv('IMAP_CONNECTION_RETRIES', getProviderAwareDefault(2, 1)));
  const retryDelayMs = Math.max(0, parseNumberEnv('IMAP_RETRY_DELAY_MS', 1500));
  let lastError;

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await connectOnce(config);
    } catch (err) {
      lastError = err;
      if (attempt >= attempts || !isRetryableConnectionError(err)) {
        throw buildConnectionError(err, 'IMAP', config.host, attempts);
      }
      await sleep(retryDelayMs * attempt);
    }
  }

  throw buildConnectionError(lastError, 'IMAP', config.host, attempts);
}

// Open mailbox and return promise
function openBox(imap, mailbox, readOnly = false) {
  return new Promise((resolve, reject) => {
    imap.openBox(mailbox, readOnly, (err, box) => {
      if (err) {
        const msg = normalizeErrorMessage(err);
        // 某些邮箱服务器（如搜狐）返回非 RFC-3501 标准的 LIST/LSUB 响应，
        // node-imap 在 openBox 过程中解析失败。提供清晰错误信息。
        if (containsAny(msg, ['unexpected', 'parse', 'bad server', 'invalid'])) {
          // 搜狐邮箱：尝试直接发 SELECT 命令绕过 LIST
          if (isSohuProvider()) {
            // node-imap 的 openBox 内部先 LIST 再 SELECT；
            // 如果 LIST 解析失败但 monkey-patch 吞掉了异常，openBox 可能还是成功的。
            // 这里的 err 说明 SELECT 本身也失败了，给出更具体的提示。
            reject(new Error(
              `IMAP 打开邮箱 "${mailbox}" 失败：搜狐邮箱服务器返回了非标准格式的响应。` +
              `当前已启用协议兼容补丁（monkey-patch），但仍无法完成 SELECT 操作。` +
              `建议：1）确认搜狐邮箱网页端已开启 IMAP 服务；` +
              `2）检查授权码是否正确（非网页登录密码）；` +
              `3）如果反复失败，搜狐 IMAP 服务可能暂时不稳定，请稍后重试。原始错误：${msg}`
            ));
          } else {
            reject(new Error(
              `IMAP 打开邮箱 "${mailbox}" 失败：服务器返回了非标准格式的响应，底层 IMAP 库无法解析。` +
              `这在部分邮箱服务商（如搜狐）上已知存在。原始错误：${msg}`
            ));
          }
        } else {
          reject(err);
        }
      } else {
        resolve(box);
      }
    });
  });
}

// Search for messages
function searchMessages(imap, criteria, fetchOptions) {
  return new Promise((resolve, reject) => {
    imap.search(criteria, (err, results) => {
      if (err) {
        reject(err);
        return;
      }

      if (!results || results.length === 0) {
        resolve([]);
        return;
      }

      const fetch = imap.fetch(results, fetchOptions);
      const messages = [];

      fetch.on('message', (msg) => {
        const parts = [];

        msg.on('body', (stream, info) => {
          let buffer = '';

          stream.on('data', (chunk) => {
            buffer += chunk.toString('utf8');
          });

          stream.once('end', () => {
            parts.push({ which: info.which, body: buffer });
          });
        });

        msg.once('attributes', (attrs) => {
          parts.forEach((part) => {
            part.attributes = attrs;
          });
        });

        msg.once('end', () => {
          if (parts.length > 0) {
            messages.push(parts[0]);
          }
        });
      });

      fetch.once('error', (fetchError) => {
        reject(fetchError);
      });

      fetch.once('end', () => {
        resolve(messages);
      });
    });
  });
}

// Parse email from raw buffer
async function parseEmail(bodyStr, includeAttachments = false) {
  const parsed = await simpleParser(bodyStr);

  return {
    from: parsed.from?.text || 'Unknown',
    to: parsed.to?.text,
    subject: parsed.subject || '(no subject)',
    date: parsed.date,
    text: parsed.text,
    html: parsed.html,
    snippet: parsed.text
      ? parsed.text.slice(0, 200)
      : (parsed.html ? parsed.html.slice(0, 200).replace(/<[^>]*>/g, '') : ''),
    attachments: parsed.attachments?.map((a) => ({
      filename: a.filename,
      contentType: a.contentType,
      size: a.size,
      content: includeAttachments ? a.content : undefined,
      cid: a.cid,
    })),
  };
}

// Check for new/unread emails
async function checkEmails(mailbox = DEFAULT_MAILBOX, limit = 10, recentTime = null, unreadOnly = false) {
  const imap = await connect();

  try {
    await openBox(imap, mailbox, true);

    // Build search criteria
    const searchCriteria = unreadOnly ? ['UNSEEN'] : ['ALL'];

    if (recentTime) {
      const sinceDate = parseRelativeTime(recentTime);
      searchCriteria.push(['SINCE', sinceDate]);
    }

    // Fetch messages sorted by date (newest first)
    const fetchOptions = {
      bodies: [''],
      markSeen: false,
    };

    const messages = await searchMessages(imap, searchCriteria, fetchOptions);

    // Sort by date (newest first) - parse from message attributes
    const sortedMessages = messages.sort((a, b) => {
      const dateA = a.attributes.date ? new Date(a.attributes.date) : new Date(0);
      const dateB = b.attributes.date ? new Date(b.attributes.date) : new Date(0);
      return dateB - dateA;
    }).slice(0, limit);

    const results = [];

    for (const item of sortedMessages) {
      const bodyStr = item.body;
      const parsed = await parseEmail(bodyStr);

      results.push({
        uid: item.attributes.uid,
        ...parsed,
        flags: item.attributes.flags,
      });
    }

    return results;
  } finally {
    imap.end();
  }
}

// Fetch full email by UID
async function fetchEmail(uid, mailbox = DEFAULT_MAILBOX) {
  const imap = await connect();

  try {
    await openBox(imap, mailbox, true);

    const searchCriteria = [['UID', uid]];
    const fetchOptions = {
      bodies: [''],
      markSeen: false,
    };

    const messages = await searchMessages(imap, searchCriteria, fetchOptions);

    if (messages.length === 0) {
      throw new Error(`Message UID ${uid} not found`);
    }

    const item = messages[0];
    const parsed = await parseEmail(item.body);

    return {
      uid: item.attributes.uid,
      ...parsed,
      flags: item.attributes.flags,
    };
  } finally {
    imap.end();
  }
}

// Download attachments from email
async function downloadAttachments(uid, mailbox = DEFAULT_MAILBOX, outputDir = '.', specificFilename = null) {
  const imap = await connect();

  try {
    await openBox(imap, mailbox, true);

    const searchCriteria = [['UID', uid]];
    const fetchOptions = {
      bodies: [''],
      markSeen: false,
    };

    const messages = await searchMessages(imap, searchCriteria, fetchOptions);

    if (messages.length === 0) {
      throw new Error(`Message UID ${uid} not found`);
    }

    const item = messages[0];
    const parsed = await parseEmail(item.body, true);

    if (!parsed.attachments || parsed.attachments.length === 0) {
      return {
        uid,
        downloaded: [],
        message: 'No attachments found',
      };
    }

    // Create output directory if it doesn't exist
    const resolvedDir = validateWritePath(outputDir);
    if (!fs.existsSync(resolvedDir)) {
      fs.mkdirSync(resolvedDir, { recursive: true });
    }

    const downloaded = [];

    for (const attachment of parsed.attachments) {
      // If specificFilename is provided, only download matching attachment
      if (specificFilename && attachment.filename !== specificFilename) {
        continue;
      }
      if (attachment.content) {
        const filePath = path.join(resolvedDir, sanitizeFilename(attachment.filename));
        fs.writeFileSync(filePath, attachment.content);
        downloaded.push({
          filename: attachment.filename,
          path: filePath,
          size: attachment.size,
        });
      }
    }

    // If specific file was requested but not found
    if (specificFilename && downloaded.length === 0) {
      const availableFiles = parsed.attachments.map((a) => a.filename).join(', ');
      return {
        uid,
        downloaded: [],
        message: `File "${specificFilename}" not found. Available attachments: ${availableFiles}`,
      };
    }

    return {
      uid,
      downloaded,
      message: `Downloaded ${downloaded.length} attachment(s)`,
    };
  } finally {
    imap.end();
  }
}

// Parse relative time (e.g., "2h", "30m", "7d") to Date
function parseRelativeTime(timeStr) {
  const match = timeStr.match(/^(\d+)(m|h|d)$/);
  if (!match) {
    throw new Error('Invalid time format. Use: 30m, 2h, 7d');
  }

  const value = parseInt(match[1], 10);
  const unit = match[2];
  const now = new Date();

  switch (unit) {
    case 'm': // minutes
      return new Date(now.getTime() - value * 60 * 1000);
    case 'h': // hours
      return new Date(now.getTime() - value * 60 * 60 * 1000);
    case 'd': // days
      return new Date(now.getTime() - value * 24 * 60 * 60 * 1000);
    default:
      throw new Error('Unknown time unit');
  }
}

// Search emails with criteria
async function searchEmails(options) {
  const imap = await connect();

  try {
    const mailbox = options.mailbox || DEFAULT_MAILBOX;
    await openBox(imap, mailbox, true);

    const criteria = [];

    if (isTruthyOption(options.unseen)) criteria.push('UNSEEN');
    if (isTruthyOption(options.seen)) criteria.push('SEEN');
    if (options.from) criteria.push(['FROM', options.from]);
    if (options.subject) criteria.push(['SUBJECT', options.subject]);

    // Handle relative time (--recent 2h)
    if (options.recent) {
      const sinceDate = parseRelativeTime(options.recent);
      criteria.push(['SINCE', sinceDate]);
    } else {
      // Handle absolute dates
      if (options.since) criteria.push(['SINCE', options.since]);
      if (options.before) criteria.push(['BEFORE', options.before]);
    }

    // Default to all if no criteria
    if (criteria.length === 0) criteria.push('ALL');

    const fetchOptions = {
      bodies: [''],
      markSeen: false,
    };

    const messages = await searchMessages(imap, criteria, fetchOptions);
    const limit = parseInt(options.limit, 10) || 20;
    const results = [];

    // Sort by date (newest first)
    const sortedMessages = messages.sort((a, b) => {
      const dateA = a.attributes.date ? new Date(a.attributes.date) : new Date(0);
      const dateB = b.attributes.date ? new Date(b.attributes.date) : new Date(0);
      return dateB - dateA;
    }).slice(0, limit);

    for (const item of sortedMessages) {
      const parsed = await parseEmail(item.body);
      results.push({
        uid: item.attributes.uid,
        ...parsed,
        flags: item.attributes.flags,
      });
    }

    return results;
  } finally {
    imap.end();
  }
}

// Mark message(s) as read
async function markAsRead(uids, mailbox = DEFAULT_MAILBOX) {
  const imap = await connect();

  try {
    await openBox(imap, mailbox);

    const result = await new Promise((resolve, reject) => {
      imap.addFlags(uids, '\\Seen', (err) => {
        if (err) reject(err);
        else resolve({ success: true, uids, action: 'marked as read' });
      });
    });

    return result;
  } finally {
    imap.end();
  }
}

// Mark message(s) as unread
async function markAsUnread(uids, mailbox = DEFAULT_MAILBOX) {
  const imap = await connect();

  try {
    await openBox(imap, mailbox);

    const result = await new Promise((resolve, reject) => {
      imap.delFlags(uids, '\\Seen', (err) => {
        if (err) reject(err);
        else resolve({ success: true, uids, action: 'marked as unread' });
      });
    });

    return result;
  } finally {
    imap.end();
  }
}

// List all mailboxes
async function listMailboxes() {
  const imap = await connect();

  try {
    const result = await new Promise((resolve, reject) => {
      imap.getBoxes((err, boxes) => {
        if (err) {
          const msg = normalizeErrorMessage(err);
          // 某些邮箱服务器（如搜狐）返回非 RFC-3501 标准的 LIST 响应，
          // node-imap 解析失败。返回友好错误而不是崩溃。
          if (containsAny(msg, ['unexpected', 'parse', 'bad server', 'invalid'])) {
            resolve([{
              name: 'INBOX',
              delimiter: '/',
              attributes: [],
              note: `无法列出完整邮箱列表：服务器返回了非标准 LIST 响应（${msg}）。仅返回默认 INBOX，请直接使用 INBOX 操作邮件。`,
            }]);
          } else {
            reject(err);
          }
        } else {
          resolve(formatMailboxTree(boxes));
        }
      });
    });

    return result;
  } finally {
    imap.end();
  }
}

// Format mailbox tree recursively
function formatMailboxTree(boxes, prefix = '') {
  const result = [];
  for (const [name, info] of Object.entries(boxes)) {
    const fullName = prefix ? `${prefix}${info.delimiter}${name}` : name;
    result.push({
      name: fullName,
      delimiter: info.delimiter,
      attributes: info.attribs,
    });

    if (info.children) {
      result.push(...formatMailboxTree(info.children, fullName));
    }
  }
  return result;
}

// Main CLI handler
async function main() {
  const { command, options, positional } = parseArgs();

  try {
    let result;

    switch (command) {
      case 'check':
        result = await checkEmails(
          options.mailbox || DEFAULT_MAILBOX,
          parseInt(options.limit, 10) || 10,
          options.recent || null,
          isTruthyOption(options.unseen)
        );
        break;

      case 'fetch':
        if (!positional[0]) {
          throw new Error('UID required: node imap.js fetch <uid>');
        }
        result = await fetchEmail(positional[0], options.mailbox);
        break;

      case 'download':
        if (!positional[0]) {
          throw new Error('UID required: node imap.js download <uid>');
        }
        result = await downloadAttachments(positional[0], options.mailbox, options.dir || '.', options.file || null);
        break;

      case 'search':
        result = await searchEmails(options);
        break;

      case 'mark-read':
        if (positional.length === 0) {
          throw new Error('UID(s) required: node imap.js mark-read <uid> [uid2...]');
        }
        result = await markAsRead(positional, options.mailbox);
        break;

      case 'mark-unread':
        if (positional.length === 0) {
          throw new Error('UID(s) required: node imap.js mark-unread <uid> [uid2...]');
        }
        result = await markAsUnread(positional, options.mailbox);
        break;

      case 'list-mailboxes':
        result = await listMailboxes();
        break;

      default:
        console.log(JSON.stringify({ success: false, error_code: 1, message: `Unknown command: ${command}. Available: check, fetch, download, search, mark-read, mark-unread, list-mailboxes` }, null, 2));
        process.exit(1);
    }

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.log(JSON.stringify({ success: false, error_code: 1, message: err.message }, null, 2));
    process.exit(1);
  }
}

main();
