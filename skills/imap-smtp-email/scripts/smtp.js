#!/usr/bin/env node

/**
 * SMTP Email CLI
 * Send email via SMTP protocol. Works with Gmail, Outlook, 163.com, and any standard SMTP server.
 * Supports attachments, HTML content, and multiple recipients.
 */

const nodemailer = require('nodemailer');
const path = require('path');
const os = require('os');
const fs = require('fs');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const NETEASE_DOMAINS = ['163.com', 'vip.163.com', '126.com', 'vip.126.com', '188.com', 'vip.188.com', 'yeah.net'];
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
  'ECONNECTION',
  'EDNS',
]);

function validateReadPath(inputPath) {
  let realPath;
  try {
    realPath = fs.realpathSync(inputPath);
  } catch {
    realPath = path.resolve(inputPath);
  }

  const allowedDirsStr = process.env.ALLOWED_READ_DIRS;
  if (!allowedDirsStr) {
    throw new Error('ALLOWED_READ_DIRS not set in .env. File read operations are disabled.');
  }

  const allowedDirs = allowedDirsStr.split(',').map((d) =>
    path.resolve(d.trim().replace(/^~/, os.homedir()))
  );

  const allowed = allowedDirs.some((dir) =>
    realPath === dir || realPath.startsWith(dir + path.sep)
  );

  if (!allowed) {
    throw new Error(`Access denied: '${inputPath}' is outside allowed read directories`);
  }

  return realPath;
}

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
      || process.env.SMTP_HOST
      || process.env.IMAP_HOST
      || process.env.SMTP_USER
      || process.env.IMAP_USER
      || ''
  ).trim().toLowerCase();
}

function isNeteaseProvider() {
  const identity = getConfiguredIdentity();
  return NETEASE_DOMAINS.some((domain) =>
    identity === domain || identity.endsWith(`.${domain}`) || identity.endsWith(`@${domain}`) || identity.includes(domain)
  );
}

function getProviderAwareDefault(neteaseValue, standardValue) {
  return isNeteaseProvider() ? neteaseValue : standardValue;
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
  const responseCode = Number(err && err.responseCode ? err.responseCode : 0);
  return responseCode === 535 || containsAny(message, [
    'auth',
    'invalid login',
    'login failed',
    'authentication failed',
    'bad credentials',
    '535',
    '535 error',
  ]);
}

/**
 * 检测网易系邮箱"不安全登录"风控拦截错误。
 * 与 isAuthError（密码/授权码错误）不同，这种错误通常是风控系统拒绝连接，
 * 常见原因：未声明客户端身份、代理/VPN、频繁重试等。
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
    'connection closed',
    'client network socket disconnected',
    'greeting never received',
    'connection reset',
    'read econnreset',
  ]);
}

function buildTlsOptions(host) {
  const tls = {
    rejectUnauthorized: parseBooleanEnv('SMTP_REJECT_UNAUTHORIZED', true),
  };

  const explicitServername = String(process.env.SMTP_SERVERNAME || '').trim();
  const servername = explicitServername || host;
  if (servername && !isIpLiteral(servername)) {
    tls.servername = servername;
  }

  const minVersion = String(process.env.SMTP_TLS_MIN_VERSION || '').trim();
  if (minVersion) {
    tls.minVersion = minVersion;
  }

  return tls;
}

function buildConnectionError(err, host, attempts) {
  const message = normalizeErrorMessage(err);
  const hostLabel = host || '未配置主机';
  const attemptNote = attempts > 1 ? ` 已自动重试 ${attempts} 次。` : '';

  if (isCertificateError(err)) {
    return new Error(
      `SMTP SSL 证书校验失败（${hostLabel}）。如果你连接的是官方邮箱域名，这通常表示本机代理/安全软件替换了证书，或系统时间/根证书异常；如果你连接的是自建网关，可将 SMTP_REJECT_UNAUTHORIZED=false 后重试。原始错误：${message}`
    );
  }

  if (isNeteaseProvider() && isUnsafeLoginError(err)) {
    return new Error(
      `SMTP 被网易服务器判定为不安全登录（${hostLabel}）。这通常不是端口号问题，而是登录风险控制、授权码无效、代理/VPN 或短时间内频繁登录导致。请优先检查客户端授权码、网页端 SMTP 开关，并尽量避免频繁重试。原始错误：${message}`
    );
  }

  if (isNeteaseProvider() && isAuthError(err)) {
    return new Error(
      `SMTP 登录失败（${hostLabel}）。网易系邮箱通常需要先在网页端开启 SMTP，并使用客户端授权码而不是网页登录密码。原始错误：${message}`
    );
  }

  if (isRetryableConnectionError(err)) {
    return new Error(
      `SMTP 连接不稳定（${hostLabel}）：${message}。这类错误常见于邮箱服务端短时抖动、限流或本地网络波动。${attemptNote}`.trim()
    );
  }

  return new Error(`SMTP 连接失败（${hostLabel}）：${message || '未知错误'}`);
}

function formatSmtpCliError(err) {
  const message = normalizeErrorMessage(err);
  if (
    message.startsWith('Missing required option:')
    || message.startsWith('Attachment file not found:')
    || message.startsWith('Access denied:')
    || message.startsWith('Missing SMTP configuration.')
  ) {
    return message;
  }
  return buildConnectionError(err, process.env.SMTP_HOST, 1).message;
}

function resolveSmtpSecure(port) {
  if (process.env.SMTP_SECURE === undefined) {
    return port === 465;
  }
  return parseBooleanEnv('SMTP_SECURE', port === 465);
}

// Create SMTP transporter
function createTransporter() {
  const host = String(process.env.SMTP_HOST || '').trim();
  const port = parseNumberEnv('SMTP_PORT', 465);
  const secure = resolveSmtpSecure(port);
  const config = {
    host,
    port,
    secure,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
    tls: buildTlsOptions(host),
    connectionTimeout: parseNumberEnv('SMTP_CONNECTION_TIMEOUT_MS', getProviderAwareDefault(30000, 120000)),
    greetingTimeout: parseNumberEnv('SMTP_GREETING_TIMEOUT_MS', getProviderAwareDefault(30000, 30000)),
    socketTimeout: parseNumberEnv('SMTP_SOCKET_TIMEOUT_MS', getProviderAwareDefault(60000, 600000)),
    dnsTimeout: parseNumberEnv('SMTP_DNS_TIMEOUT_MS', 30000),
  };

  if (!config.host || !config.auth.user || !config.auth.pass) {
    throw new Error('Missing SMTP configuration. Please set SMTP_HOST, SMTP_USER, and SMTP_PASS in .env');
  }

  return nodemailer.createTransport(config);
}

async function runWithTransport(action) {
  const transporter = createTransporter();
  try {
    return await action(transporter);
  } finally {
    transporter.close();
  }
}

async function runSmtpActionWithRetry(action) {
  const attempts = Math.max(1, parseNumberEnv('SMTP_CONNECTION_RETRIES', getProviderAwareDefault(2, 1)));
  const retryDelayMs = Math.max(0, parseNumberEnv('SMTP_RETRY_DELAY_MS', 1500));
  let lastError;

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await runWithTransport(action);
    } catch (err) {
      lastError = err;
      if (attempt >= attempts || !isRetryableConnectionError(err)) {
        throw buildConnectionError(err, process.env.SMTP_HOST, attempts);
      }
      await sleep(retryDelayMs * attempt);
    }
  }

  throw buildConnectionError(lastError, process.env.SMTP_HOST, attempts);
}

// Send email
async function sendEmail(options) {
  const mailOptions = {
    from: options.from || process.env.SMTP_FROM || process.env.SMTP_USER,
    to: options.to,
    cc: options.cc || undefined,
    bcc: options.bcc || undefined,
    subject: options.subject || '(no subject)',
    text: options.text || undefined,
    html: options.html || undefined,
    attachments: options.attachments || [],
  };

  // If neither text nor html provided, use default text
  if (!mailOptions.text && !mailOptions.html) {
    mailOptions.text = options.body || '';
  }

  const info = await runSmtpActionWithRetry((transporter) => transporter.sendMail(mailOptions));

  return {
    success: true,
    messageId: info.messageId,
    response: info.response,
    to: mailOptions.to,
  };
}

// Read file content for attachments
function readAttachment(filePath) {
  validateReadPath(filePath);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Attachment file not found: ${filePath}`);
  }
  return {
    filename: path.basename(filePath),
    path: path.resolve(filePath),
  };
}

// Send email with file content
async function sendEmailWithContent(options) {
  // Handle attachments
  if (options.attach) {
    const attachFiles = options.attach.split(',').map((f) => f.trim());
    options.attachments = attachFiles.map((f) => readAttachment(f));
  }

  return sendEmail(options);
}

// Test SMTP connection
async function testConnection() {
  await runSmtpActionWithRetry((transporter) => transporter.verify());
  return {
    success: true,
    message: 'SMTP connection successful',
  };
}

// Main CLI handler
async function main() {
  const { command, options } = parseArgs();

  try {
    let result;

    switch (command) {
      case 'send':
        if (!options.to) {
          throw new Error('Missing required option: --to <email>');
        }
        if (!options.subject && !options['subject-file']) {
          throw new Error('Missing required option: --subject <text> or --subject-file <file>');
        }

        // Read subject from file if specified
        if (options['subject-file']) {
          validateReadPath(options['subject-file']);
          options.subject = fs.readFileSync(options['subject-file'], 'utf8').trim();
        }

        const wantsHtml = isTruthyOption(options.html)
          || String(options.content_type || '').trim().toLowerCase() === 'html';

        // Read body from file if specified
        if (options['body-file']) {
          validateReadPath(options['body-file']);
          const content = fs.readFileSync(options['body-file'], 'utf8');
          if (options['body-file'].endsWith('.html') || wantsHtml) {
            options.html = content;
            delete options.text;
          } else {
            options.text = content;
            delete options.html;
          }
        } else if (options['html-file']) {
          validateReadPath(options['html-file']);
          options.html = fs.readFileSync(options['html-file'], 'utf8');
          delete options.text;
        } else if (options.body) {
          if (wantsHtml) {
            options.html = options.body;
            delete options.text;
          } else {
            options.text = options.body;
            delete options.html;
          }
        }

        result = await sendEmailWithContent(options);
        break;

      case 'test':
        result = await testConnection();
        break;

      default:
        console.log(JSON.stringify({ success: false, error_code: 1, message: `Unknown command: ${command}. Available: send, test` }, null, 2));
        process.exit(1);
    }

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.log(JSON.stringify({ success: false, error_code: 1, message: err.message }, null, 2));
    process.exit(1);
  }
}

main();
