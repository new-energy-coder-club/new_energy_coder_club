#!/usr/bin/env node

/**
 * resolve-account.cjs — imap-smtp-email 账号解析入口
 *
 * 在执行 smtp.js / imap.js 之前，先解析要使用的邮箱账号：
 *
 *   1. 调 4230 接口（authorized-email-platforms）拉用户全部绑定的私人邮箱
 *   2. 邮箱选择逻辑：
 *      - 用户命令中通过 --account-email 明确指定了邮箱 → 使用该邮箱
 *      - 未指定 → 从绑定列表中选一个（排除 public_mail）
 *      - 没有绑定 → 返回错误提示需要先绑定
 *   3. 调凭证刷新脚本（macOS/Linux: get-token.sh, Windows: get-token.ps1）写入 .env
 *   4. 继续执行原有命令
 *
 * 用法：
 *   node resolve-account.cjs send [--account-email your@163.com] --to ... --subject ... --body ...
 *   node resolve-account.cjs send [--account-platform sina_mail] --to ... --subject ... --body ...
 *   node resolve-account.cjs check [--account-email your@163.com] --limit 10
 *   node resolve-account.cjs resolve [--account-email your@163.com]   ← 仅解析，不执行后续命令
 *
 *   --account-platform 支持：用户只说"新浪邮箱"等模糊指定时，LLM 传入 platform 标识，
 *   脚本从绑定列表中匹配对应平台的邮箱。
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const { spawnSync, spawn } = require('child_process');

const SKILL_DIR = path.resolve(__dirname, '..');
const IS_WINDOWS = process.platform === 'win32';
const GET_TOKEN_SCRIPT = IS_WINDOWS
  ? path.join(SKILL_DIR, 'get-token.ps1')
  : path.join(SKILL_DIR, 'get-token.sh');
const SMTP_JS = path.join(__dirname, 'smtp.js');
const IMAP_JS = path.join(__dirname, 'imap.js');
const ENV_FILE = path.join(SKILL_DIR, '.env');

// 个人邮箱平台白名单（与拦截器一致，排除 public_mail 等非个人邮箱）
const PERSONAL_PLATFORMS = new Set([
  '163_mail', 'qq_mail', 'gmail', 'outlook', 'sina_mail', 'sohu_mail',
]);

// platform → 邮箱域名（用于反查）
const PLATFORM_DOMAIN_MAP = {
  '163_mail': '163.com',
  'qq_mail': 'qq.com',
  'gmail': 'gmail.com',
  'outlook': 'outlook.com',
  'sina_mail': 'sina.com',
  'sohu_mail': 'sohu.com',
};

// 邮箱域名 → platform（用于正查）
const DOMAIN_PLATFORM_MAP = {
  '163.com': '163_mail',
  'vip.163.com': '163_mail',
  '126.com': '163_mail',
  'vip.126.com': '163_mail',
  '188.com': '163_mail',
  'vip.188.com': '163_mail',
  'yeah.net': '163_mail',
  'qq.com': 'qq_mail',
  'foxmail.com': 'qq_mail',
  'vip.qq.com': 'qq_mail',
  'exmail.qq.com': 'qq_mail',
  'gmail.com': 'gmail',
  'outlook.com': 'outlook',
  'hotmail.com': 'outlook',
  'live.com': 'outlook',
  'live.cn': 'outlook',
  'sina.com': 'sina_mail',
  'sina.cn': 'sina_mail',
  'vip.sina.com': 'sina_mail',
  'sohu.com': 'sohu_mail',
};

// 中文别名 / 自然语言简称 → platform（用于 --account-platform 模糊匹配）
const ALIAS_PLATFORM_MAP = {
  // 网易系
  '163_mail': '163_mail',
  '163': '163_mail',
  '网易': '163_mail',
  '网易邮箱': '163_mail',
  '163邮箱': '163_mail',
  '126邮箱': '163_mail',
  'netease': '163_mail',
  // QQ 系
  'qq_mail': 'qq_mail',
  'qq': 'qq_mail',
  'qq邮箱': 'qq_mail',
  'foxmail': 'qq_mail',
  'foxmail邮箱': 'qq_mail',
  '腾讯邮箱': 'qq_mail',
  // Gmail
  'gmail': 'gmail',
  'gmail邮箱': 'gmail',
  '谷歌邮箱': 'gmail',
  '谷歌': 'gmail',
  'google': 'gmail',
  // Outlook
  'outlook': 'outlook',
  'outlook邮箱': 'outlook',
  '微软邮箱': 'outlook',
  '微软': 'outlook',
  'hotmail': 'outlook',
  'live': 'outlook',
  // 新浪
  'sina_mail': 'sina_mail',
  'sina': 'sina_mail',
  '新浪': 'sina_mail',
  '新浪邮箱': 'sina_mail',
  // 搜狐
  'sohu_mail': 'sohu_mail',
  'sohu': 'sohu_mail',
  '搜狐': 'sohu_mail',
  '搜狐邮箱': 'sohu_mail',
};

const HTTP_REQUEST_TIMEOUT = 15000;

// ──────────────────────────────────────
// 通用工具
// ──────────────────────────────────────

function outputJson(payload) {
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
}

function success(payload = {}) {
  outputJson({ success: true, ...payload });
  process.exit(0);
}

function fail(message, errorCode = 1, extra = {}) {
  outputJson({ success: false, error_code: errorCode, message, ...extra });
  process.exit(1);
}

function getOptionValue(args, flag) {
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === flag) {
      return args[i + 1] || '';
    }
  }
  return '';
}

function removeFlagWithValue(args, flag) {
  const result = [];
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === flag) {
      i += 1; // skip value
      continue;
    }
    result.push(args[i]);
  }
  return result;
}

// ──────────────────────────────────────
// 调 4230 接口拉全部绑定的私人邮箱
// ──────────────────────────────────────

function getProxyPort() {
  const envPort = process.env.AUTH_GATEWAY_PORT;
  if (envPort) {
    const parsed = parseInt(envPort, 10);
    if (!isNaN(parsed) && parsed > 0) return parsed;
  }
  return 19000;
}

function getRemoteBaseUrl() {
  return process.env.BUILD_ENV === 'test'
    ? 'https://jprx.sparta.html5.qq.com'
    : 'https://jprx.m.qq.com';
}

/**
 * 通过 Auth Gateway 代理查询已绑定的个人邮箱列表
 *
 * @returns {Promise<Array<{platform: string, email: string, auth_type?: string}>>}
 */
async function fetchBoundPersonalEmails() {
  const proxyPort = getProxyPort();
  const remoteBaseUrl = getRemoteBaseUrl();
  const remoteUrl = `${remoteBaseUrl}/data/4230/forward`;

  const bodyStr = JSON.stringify({});

  return new Promise((resolve, reject) => {
    const request = http.request({
      host: '127.0.0.1',
      port: proxyPort,
      path: '/proxy/api',
      method: 'POST',
      timeout: HTTP_REQUEST_TIMEOUT,
      headers: {
        'Remote-URL': remoteUrl,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(bodyStr),
      },
    }, (response) => {
      let rawBody = '';
      response.setEncoding('utf8');
      response.on('data', (chunk) => { rawBody += chunk; });
      response.on('end', () => {
        try {
          if (response.statusCode !== 200) {
            resolve([]);
            return;
          }
          const data = rawBody ? JSON.parse(rawBody) : null;
          if (!data || data.ret !== 0) {
            resolve([]);
            return;
          }
          // 兼容多种嵌套格式
          const respData = data?.data?.resp?.data ?? data?.data?.data ?? data?.data;
          const rawPlatforms = Array.isArray(respData?.platforms) ? respData.platforms : [];

          // 仅保留个人邮箱平台
          const personalEmails = rawPlatforms.filter(
            (p) => p.platform && PERSONAL_PLATFORMS.has(p.platform),
          );
          resolve(personalEmails);
        } catch (err) {
          resolve([]);
        }
      });
    });

    request.on('timeout', () => {
      request.destroy();
      resolve([]);
    });
    request.on('error', () => {
      resolve([]);
    });

    request.write(bodyStr);
    request.end();
  });
}

// ──────────────────────────────────────
// 调 get-token 脚本写入 .env（跨平台）
// ──────────────────────────────────────

/**
 * 根据选中的 platform 调凭证刷新脚本写入 .env
 * - Windows: powershell get-token.ps1 -Platform xxx
 * - macOS/Linux: bash get-token.sh --platform xxx
 *
 * @param {string} platform - 凭证平台标识（如 "163_mail"）
 * @param {string} [expectedEmail] - 用户指定的邮箱地址，用于刷新后校验
 * @returns {{ success: boolean, message: string, email?: string }}
 */
function refreshCredentialForPlatform(platform, expectedEmail) {
  if (!fs.existsSync(GET_TOKEN_SCRIPT)) {
    return { success: false, message: `未找到凭证刷新脚本: ${GET_TOKEN_SCRIPT}` };
  }

  try {
    let result;
    if (IS_WINDOWS) {
      result = spawnSync(
        'powershell',
        ['-ExecutionPolicy', 'Bypass', '-File', GET_TOKEN_SCRIPT, '-Platform', platform],
        { cwd: SKILL_DIR, env: process.env, timeout: 15000, stdio: ['ignore', 'pipe', 'pipe'] },
      );
    } else {
      result = spawnSync(
        'bash',
        [GET_TOKEN_SCRIPT, '--platform', platform],
        { cwd: SKILL_DIR, env: process.env, timeout: 15000, stdio: ['ignore', 'pipe', 'pipe'] },
      );
    }

    const stdout = String(result.stdout || '').replace(/^\uFEFF/, '').trim();
    const stderr = String(result.stderr || '').replace(/^\uFEFF/, '').trim();

    if (result.error) {
      return { success: false, message: result.error.message || '凭证刷新脚本执行失败' };
    }

    // 尝试解析 stdout 中的 JSON
    let payload = null;
    try {
      payload = JSON.parse(stdout);
    } catch (e) {
      // stdout 不是 JSON
    }

    if ((result.status || 0) === 0 && fs.existsSync(ENV_FILE)) {
      // 校验：如果用户指定了邮箱，检查凭证刷新后 .env 中的邮箱是否与用户指定的一致
      if (expectedEmail) {
        const refreshedEnv = parseEnvFile(ENV_FILE);
        const refreshedEmail = (refreshedEnv.SMTP_USER || refreshedEnv.SMTP_FROM || refreshedEnv.IMAP_USER || '').trim().toLowerCase();
        const normalizedExpected = expectedEmail.trim().toLowerCase();
        if (refreshedEmail && refreshedEmail !== normalizedExpected) {
          return {
            success: false,
            message: `凭证服务返回的邮箱 (${refreshedEmail}) 与指定的邮箱 (${normalizedExpected}) 不一致。该平台 (${platform}) 可能绑定的是另一个邮箱账号。请检查绑定状态。`,
            email: refreshedEmail,
          };
        }
      }

      return {
        success: true,
        message: payload?.message || '已刷新凭证',
        email: payload?.email || undefined,
      };
    }

    return {
      success: false,
      message: payload?.message || stderr || stdout || '凭证刷新失败',
    };
  } catch (err) {
    return { success: false, message: err.message || '凭证刷新异常' };
  }
}

// ──────────────────────────────────────
// 解析 .env 获取当前配置的邮箱
// ──────────────────────────────────────

function parseEnvFile(envPath) {
  if (!fs.existsSync(envPath)) return {};
  // 清除可能的 UTF-8 BOM（Windows PowerShell 5.x Set-Content -Encoding UTF8 会写入 BOM）
  const content = fs.readFileSync(envPath, 'utf8').replace(/^\uFEFF/, '');
  const env = {};
  for (const rawLine of content.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    const sep = line.indexOf('=');
    if (sep === -1) continue;
    const key = line.slice(0, sep).trim();
    let value = line.slice(sep + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    env[key] = value;
  }
  return env;
}

function getCurrentConfiguredEmail() {
  const env = parseEnvFile(ENV_FILE);
  return (env.SMTP_USER || env.SMTP_FROM || env.IMAP_USER || '').trim().toLowerCase();
}

// ──────────────────────────────────────
// 邮箱匹配逻辑
// ──────────────────────────────────────

/**
 * 根据邮箱地址找到对应的 platform
 */
function findPlatformForEmail(email, boundEmails) {
  const normalizedEmail = email.trim().toLowerCase();

  // 先从已绑定列表中精确匹配
  for (const item of boundEmails) {
    if (item.email && item.email.toLowerCase() === normalizedEmail) {
      return item.platform;
    }
  }

  // 回退：根据域名推断 platform
  const domain = normalizedEmail.split('@')[1];
  if (domain && DOMAIN_PLATFORM_MAP[domain]) {
    return DOMAIN_PLATFORM_MAP[domain];
  }

  return null;
}

/**
 * 将 --account-platform 传入的别名/标识解析为标准 platform
 */
function resolvePlatformAlias(alias) {
  if (!alias) return null;
  const normalized = alias.trim().toLowerCase();
  return ALIAS_PLATFORM_MAP[normalized] || null;
}

/**
 * 根据 platform 从已绑定列表中查找对应邮箱
 */
function findEmailForPlatform(platform, boundEmails) {
  for (const item of boundEmails) {
    if (item.platform === platform && item.email) {
      return item;
    }
  }
  return null;
}

// ──────────────────────────────────────
// IMAP 命令映射
// ──────────────────────────────────────

const IMAP_COMMANDS = new Set([
  'check', 'search', 'fetch', 'download',
  'mark-read', 'mark-unread', 'list-mailboxes',
  // 带 inbox- 前缀的别名（SKILL.md 文档使用此格式，LLM 常生成此格式）
  'inbox-check', 'inbox-search', 'inbox-fetch', 'inbox-download',
  'inbox-mark-read', 'inbox-mark-unread', 'inbox-list-mailboxes',
]);

const SMTP_COMMANDS = new Set(['send', 'test']);

/**
 * 将带 inbox- 前缀的命令归一化为 imap.js 接受的命令名
 * inbox-check → check, inbox-search → search, 等
 */
function normalizeCommand(cmd) {
  if (cmd.startsWith('inbox-')) {
    return cmd.slice('inbox-'.length);
  }
  return cmd;
}

// ──────────────────────────────────────
// 主逻辑
// ──────────────────────────────────────

async function main() {
  const allArgs = process.argv.slice(2);
  const command = allArgs[0] || 'resolve';
  const restArgs = allArgs.slice(1);

  // 提取 --account-email 参数
  const accountEmail = getOptionValue(restArgs, '--account-email');
  // 提取 --account-platform 参数（支持中文别名/平台标识）
  const accountPlatformRaw = getOptionValue(restArgs, '--account-platform');
  let cleanArgs = removeFlagWithValue(restArgs, '--account-email');
  cleanArgs = removeFlagWithValue(cleanArgs, '--account-platform');

  // 步骤 1：拉全部绑定的私人邮箱
  const boundEmails = await fetchBoundPersonalEmails();

  // 步骤 2：决定使用哪个邮箱
  let selectedPlatform = null;
  let selectedEmail = null;

  if (accountEmail) {
    // ── 用户明确指定了邮箱地址 ──
    selectedPlatform = findPlatformForEmail(accountEmail, boundEmails);
    selectedEmail = accountEmail.trim().toLowerCase();

    if (!selectedPlatform) {
      fail(
        `指定的邮箱 ${accountEmail} 无法匹配到已绑定的个人邮箱平台。请先在集成面板中绑定该邮箱。`,
        2,
        {
          requested_email: accountEmail,
          bound_emails: boundEmails.map((e) => ({ platform: e.platform, email: e.email })),
        },
      );
    }
  } else if (accountPlatformRaw) {
    // ── 用户通过平台别名指定（如 "新浪邮箱"、"sina_mail"）──
    const resolvedPlatform = resolvePlatformAlias(accountPlatformRaw);
    if (!resolvedPlatform) {
      fail(
        `无法识别的邮箱平台别名: "${accountPlatformRaw}"。支持的别名: 163/网易邮箱/qq/QQ邮箱/gmail/谷歌邮箱/outlook/微软邮箱/sina/新浪邮箱/sohu/搜狐邮箱`,
        2,
        { requested_platform: accountPlatformRaw },
      );
    }

    const matched = findEmailForPlatform(resolvedPlatform, boundEmails);
    if (!matched) {
      fail(
        `你指定了"${accountPlatformRaw}"（${resolvedPlatform}），但当前没有绑定该平台的邮箱。请先在集成面板中绑定。`,
        2,
        {
          requested_platform: accountPlatformRaw,
          resolved_platform: resolvedPlatform,
          bound_emails: boundEmails.map((e) => ({ platform: e.platform, email: e.email })),
        },
      );
    }

    selectedPlatform = matched.platform;
    selectedEmail = matched.email;
  } else if (boundEmails.length === 0) {
    // ── 没有绑定任何邮箱 ──
    if (command === 'resolve') {
      // 仅解析模式，返回状态
      success({
        status: 'no_binding',
        message: '当前没有绑定任何个人邮箱，请先在集成面板中绑定邮箱。',
        bound_emails: [],
      });
    }
    fail(
      '当前没有绑定任何个人邮箱，请先在集成面板中绑定邮箱后重试。',
      2,
      { bound_emails: [] },
    );
  } else if (boundEmails.length === 1) {
    // ── 恰好 1 个绑定 → 自动选择 ──
    selectedPlatform = boundEmails[0].platform;
    selectedEmail = boundEmails[0].email;
  } else {
    // ── 多个绑定但未指定 → 选择第一个 ──
    // 注意：正常流程中如果有多个绑定，拦截器会弹选择卡片让用户选择后传入 --account-email
    // 这里是兜底逻辑
    selectedPlatform = boundEmails[0].platform;
    selectedEmail = boundEmails[0].email;
  }

  // 如果是 resolve 命令，仅输出解析结果
  if (command === 'resolve') {
    success({
      status: 'resolved',
      selected_platform: selectedPlatform,
      selected_email: selectedEmail,
      bound_emails: boundEmails.map((e) => ({ platform: e.platform, email: e.email })),
    });
  }

  // 步骤 3：决定是否需要刷新凭证
  // - 邮箱不一致 → 必须刷新
  // - 邮箱一致但 TOKEN_SOURCE=credential_service → 也要刷新（凭证服务的 access_token 有时效性）
  // - 邮箱一致且 TOKEN_SOURCE=manual_token → 跳过刷新（用户手动设置的，信任不过期）
  const currentEmail = getCurrentConfiguredEmail();
  const currentEnv = parseEnvFile(ENV_FILE);
  const tokenSource = (currentEnv.TOKEN_SOURCE || '').trim();
  const emailMatches = currentEmail && currentEmail === selectedEmail.toLowerCase();
  const needRefresh = !emailMatches || tokenSource !== 'manual_token';

  if (needRefresh) {
    // 调凭证刷新脚本刷新凭证写入 .env，传入 selectedEmail 用于校验
    const refreshResult = refreshCredentialForPlatform(selectedPlatform, selectedEmail);
    if (!refreshResult.success) {
      fail(
        `切换到邮箱 ${selectedEmail} (${selectedPlatform}) 的凭证刷新失败：${refreshResult.message}`,
        2,
        {
          selected_platform: selectedPlatform,
          selected_email: selectedEmail,
          refresh_error: refreshResult.message,
        },
      );
    }
  }

  // 步骤 4：执行后续命令
  if (SMTP_COMMANDS.has(command)) {
    // 执行 smtp.js
    const child = spawn('node', [SMTP_JS, command, ...cleanArgs], {
      cwd: SKILL_DIR,
      env: process.env,
      stdio: 'inherit',
    });
    child.on('close', (code) => process.exit(code || 0));
    child.on('error', (err) => {
      fail(`执行 smtp.js 失败: ${err.message}`, 1);
    });
  } else if (IMAP_COMMANDS.has(command)) {
    // 执行 imap.js（归一化命令名，去掉 inbox- 前缀）
    const imapCmd = normalizeCommand(command);
    const child = spawn('node', [IMAP_JS, imapCmd, ...cleanArgs], {
      cwd: SKILL_DIR,
      env: process.env,
      stdio: 'inherit',
    });
    child.on('close', (code) => process.exit(code || 0));
    child.on('error', (err) => {
      fail(`执行 imap.js 失败: ${err.message}`, 1);
    });
  } else {
    fail(`未知命令: ${command}，支持的命令: send, test, inbox-check (check), inbox-search (search), inbox-fetch (fetch), inbox-download (download), inbox-mark-read (mark-read), inbox-mark-unread (mark-unread), inbox-list-mailboxes (list-mailboxes), resolve`, 1);
  }
}

main().catch((err) => {
  fail(err.message || String(err), 999);
});
