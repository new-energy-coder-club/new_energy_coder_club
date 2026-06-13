#!/usr/bin/env node

/**
 * public-skill/scripts/router.cjs
 *
 * 平台公邮（Public Email）独立路由入口。
 * 从 email-skill/scripts/router.cjs 中提取的公邮逻辑。
 *
 * 功能：
 *   - 通过 Auth Gateway 代理访问 jprx.m.qq.com 平台接口
 *   - 支持绑定检查、发送验证码、验证绑定、发送邮件
 *   - 仅支持发送到用户自己的邮箱（不支持第三方收件人）
 *   - 仅支持纯文本内容（不支持 HTML/附件/抄送/密送）
 *
 * 命令：
 *   bind-check       检查邮箱是否已绑定平台公邮
 *   bind-send-code   向指定邮箱发送绑定验证码
 *   bind-verify      使用验证码完成邮箱绑定
 *   send             发送邮件（仅平台公邮通道）
 *   capabilities     输出当前 public-skill 能力信息
 *   help             显示帮助信息
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

// BUILD_ENV=test 时走测试环境，其他情况走现网
const REMOTE_BASE_URL = process.env.BUILD_ENV === 'test'
  ? 'https://jprx.sparta.html5.qq.com'
  : 'https://jprx.m.qq.com';

// 超时配置（毫秒）
const HTTP_REQUEST_TIMEOUT = 30000; // HTTP 请求 30 秒超时

// ──────────────────────────────────────
// 通用工具函数
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

function toLower(value) {
  return String(value || '').trim().toLowerCase();
}

function hasFlag(args, flag) {
  return args.includes(flag);
}

function getOptionValue(args, flag) {
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] === flag) {
      return args[index + 1] || '';
    }
  }
  return '';
}

function readTextOption(sendArgs, inlineFlag, fileFlag) {
  const inlineValue = getOptionValue(sendArgs, inlineFlag);
  if (inlineValue) {
    return inlineValue;
  }

  const filePath = getOptionValue(sendArgs, fileFlag);
  if (!filePath) {
    return '';
  }

  const resolvedPath = path.resolve(process.cwd(), filePath);
  if (!fs.existsSync(resolvedPath)) {
    fail(`文件不存在: ${filePath}`, 1);
  }
  return fs.readFileSync(resolvedPath, 'utf8');
}

// ──────────────────────────────────────
// 平台公邮参数校验
// ──────────────────────────────────────

/**
 * 检查 send 参数是否满足平台公邮的适用条件。
 * 同时满足以下条件才返回 true：
 *   1. 有 --email
 *   2. 无 --to / --cc / --bcc / --attach / --from / --html / --html-file
 *   3. content_type 为 text 或未指定
 */
function isPlatformEligible(sendArgs) {
  const email = getOptionValue(sendArgs, '--email');
  const contentType = toLower(getOptionValue(sendArgs, '--content_type') || 'text');
  if (!email) {
    return false;
  }
  if (hasFlag(sendArgs, '--to')) {
    return false;
  }
  if (hasFlag(sendArgs, '--cc') || hasFlag(sendArgs, '--bcc') || hasFlag(sendArgs, '--attach')) {
    return false;
  }
  if (hasFlag(sendArgs, '--from') || hasFlag(sendArgs, '--html') || hasFlag(sendArgs, '--html-file')) {
    return false;
  }
  if (contentType && contentType !== 'text') {
    return false;
  }
  return true;
}

/**
 * 当用户显式调用 public-skill send 时，校验是否传了不支持的参数。
 * 如果传了 --to、--cc 等，要明确报错而非静默忽略。
 */
function validatePlatformExplicit(sendArgs) {
  const unsupported = [];
  if (hasFlag(sendArgs, '--to')) {
    unsupported.push('--to（公邮仅支持发送到自己邮箱，不支持发给他人）');
  }
  if (hasFlag(sendArgs, '--cc')) {
    unsupported.push('--cc（公邮不支持抄送）');
  }
  if (hasFlag(sendArgs, '--bcc')) {
    unsupported.push('--bcc（公邮不支持密送）');
  }
  if (hasFlag(sendArgs, '--attach')) {
    unsupported.push('--attach（公邮不支持附件）');
  }
  if (hasFlag(sendArgs, '--from')) {
    unsupported.push('--from（公邮不支持自定义发件人）');
  }
  if (hasFlag(sendArgs, '--html') || hasFlag(sendArgs, '--html-file')) {
    unsupported.push('--html/--html-file（公邮不支持 HTML 内容）');
  }
  const contentType = toLower(getOptionValue(sendArgs, '--content_type') || 'text');
  if (contentType && contentType !== 'text') {
    unsupported.push(`--content_type ${contentType}（公邮仅支持纯文本）`);
  }
  if (unsupported.length > 0) {
    fail(`平台公邮不支持以下参数：\n  ${unsupported.join('\n  ')}\n请改用 email-skill send --provider personal（底层为 imap-smtp-email）来发送。`, 1);
  }
}

// ──────────────────────────────────────
// Auth Gateway 代理请求
// ──────────────────────────────────────

async function detectProxyPort() {
  if (process.env.AUTH_GATEWAY_PORT) {
    return process.env.AUTH_GATEWAY_PORT;
  }

  if (process.platform === 'linux') {
    try {
      const procVersion = fs.readFileSync('/proc/version', 'utf8');
      if (/microsoft/i.test(procVersion)) {
        const port = await runProcess('cmd.exe', ['/C', 'echo %AUTH_GATEWAY_PORT%'], { allowFailure: true });
        const output = String(port.stdout || '').replace(/\r/g, '').trim();
        if (output && output !== '%AUTH_GATEWAY_PORT%') {
          return output;
        }
      }
    } catch (error) {
      // ignore WSL detection failure
    }
  }

  return '19000';
}

async function requestPlatform(apiPath, payload) {
  const proxyPort = await detectProxyPort();
  const requestBody = JSON.stringify(payload);

  return new Promise((resolve, reject) => {
    const request = http.request({
      host: '127.0.0.1',
      port: Number(proxyPort),
      path: '/proxy/api',
      method: 'POST',
      timeout: HTTP_REQUEST_TIMEOUT,
      headers: {
        'Remote-URL': `${REMOTE_BASE_URL}${apiPath}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(requestBody),
      },
    }, (response) => {
      let rawBody = '';
      response.setEncoding('utf8');
      response.on('data', (chunk) => {
        rawBody += chunk;
      });
      response.on('end', () => {
        resolve({
          httpStatus: response.statusCode || 0,
          rawBody,
        });
      });
    });

    request.on('timeout', () => {
      request.destroy();
      reject(new Error(`平台请求超时（${HTTP_REQUEST_TIMEOUT / 1000}秒）`));
    });

    request.on('error', reject);
    request.write(requestBody);
    request.end();
  });
}

function buildPlatformRequestFailure(error) {
  return enrichPlatformFailure({
    success: false,
    error_code: 999,
    message: error && error.message ? error.message : String(error || '平台请求失败'),
  });
}

const PLATFORM_RELOGIN_CODES = new Set([21004]);
const PLATFORM_RELOGIN_HINT = '平台公邮网关提示“登录已过期”，请在 OpenClaw 主界面重新登录认证后重试。';
const PLATFORM_RELOGIN_PATTERNS = [
  '登录已过期',
  '重新登录',
  '未登录',
  'login expired',
  'session expired',
];

function requiresPlatformRelogin(result = {}) {
  if (!result || result.success) {
    return false;
  }

  const errorCode = Number(result.error_code || 0);
  if (PLATFORM_RELOGIN_CODES.has(errorCode)) {
    return true;
  }

  const message = String(result.message || '').toLowerCase();
  return PLATFORM_RELOGIN_PATTERNS.some((pattern) => message.includes(String(pattern).toLowerCase()));
}

function enrichPlatformFailure(result = {}) {
  if (!requiresPlatformRelogin(result)) {
    return result;
  }

  const originalMessage = String(result.message || '登录已过期，请重新登录');
  const message = originalMessage.includes('OpenClaw 主界面重新登录认证')
    ? originalMessage
    : `${originalMessage}。${PLATFORM_RELOGIN_HINT}`;
  const nextSteps = Array.isArray(result.next_steps) ? [...result.next_steps] : [];
  if (!nextSteps.includes('在 OpenClaw 主界面重新登录认证')) {
    nextSteps.unshift('在 OpenClaw 主界面重新登录认证');
  }

  return {
    ...result,
    message,
    relogin_required: true,
    relogin_target: 'OpenClaw',
    recovery_hint: PLATFORM_RELOGIN_HINT,
    next_steps: nextSteps,
  };
}

// ──────────────────────────────────────
// 网关响应解析
// ──────────────────────────────────────

function parseGatewayResponse(rawBody, httpStatus) {
  if (httpStatus !== 200) {
    return {
      success: false,
      error_code: 999,
      message: `HTTP请求失败，状态码: ${httpStatus}`,
    };
  }

  let parsed;
  try {
    parsed = JSON.parse(rawBody);
  } catch (error) {
    return {
      success: false,
      error_code: 999,
      message: `网关返回了无法解析的响应: ${error.message}`,
    };
  }

  if (String(parsed.ret) !== '0') {
    return {
      success: false,
      error_code: 999,
      message: `网关层错误，ret=${parsed.ret}`,
    };
  }

  const resp = (((parsed || {}).data || {}).resp || {});
  const common = resp.common || {};
  if (String(common.code) === '0') {
    return {
      success: true,
      data: resp.data || {},
      message: common.message || 'Success',
    };
  }

  return enrichPlatformFailure({
    success: false,
    error_code: Number(common.code || 999),
    message: common.message || '未知错误',
  });
}

// ──────────────────────────────────────
// 通过凭证服务获取已绑定邮箱
// ──────────────────────────────────────

/**
 * 查询当前用户在平台侧已绑定的公邮邮箱，并保留详细错误信息，供统一路由与 doctor 使用。
 *
 * @returns {Promise<{success:boolean,email?:string,error_code?:number,message:string}>}
 */
async function getBoundEmailDiagnostic() {
  try {
    const response = await requestPlatform('/data/4227/forward', {});
    const parsed = parseGatewayResponse(response.rawBody, response.httpStatus);
    if (!parsed.success) {
      return parsed;
    }

    const data = parsed.data || {};
    const extraData = data.extra_data || {};
    const email = extraData.email || extraData.email_address || data.email || data.email_address;
    if (!email) {
      return {
        success: false,
        error_code: 3,
        message: '当前未检测到已绑定的平台公邮邮箱',
      };
    }

    return {
      success: true,
      email,
      message: '已检测到平台公邮绑定邮箱',
    };
  } catch (error) {
    return buildPlatformRequestFailure(error);
  }
}

async function getBoundEmailFromCredential() {
  const diagnostic = await getBoundEmailDiagnostic();
  return diagnostic.success ? diagnostic.email : null;
}

// ──────────────────────────────────────
// 绑定状态判断
// ──────────────────────────────────────

// 平台公邮"未绑定"状态的 error_code 白名单
const PLATFORM_NOT_BOUND_CODES = new Set([3, 4001, 4002]);

function isPlatformNotBound(response) {
  if (!response || response.success) {
    return false;
  }
  const message = String(response.message || '');
  const errorCode = Number(response.error_code || 0);

  // 通过 error_code 白名单判断
  if (PLATFORM_NOT_BOUND_CODES.has(errorCode)) {
    return true;
  }

  // 通过 message 文本判断（精确匹配"未绑定"/"尚未绑定"）
  if (message.includes('尚未绑定') || message.includes('未绑定')) {
    return true;
  }

  return false;
}

/**
 * 判断平台公邮错误是否属于"可回退"类型。
 * 此函数由 email-skill 路由层在 auto 模式下调用，用于决定是否自动回退到个人邮箱。
 * public-skill 自身不执行回退逻辑，但导出此判断函数供上层使用。
 */
function isPlatformFallbackError(response) {
  if (!response || response.success) {
    return false;
  }

  const errorCode = Number(response.error_code || 0);

  // 未绑定不应触发回退，应返回绑定引导
  if (isPlatformNotBound(response)) {
    return false;
  }

  // 网关层 / 网络层错误（error_code 999 = 我们自己标记的通信故障）
  if (errorCode === 999) {
    return true;
  }

  const message = String(response.message || '');

  // 精确匹配：仅匹配确实代表"通道不可用/额度不足"的关键短语
  const EXACT_FALLBACK_PHRASES = [
    '公共域名已达日发送上限',
    '日发送上限',
    '额度不足',
    '配额不足',
    '通道不可用',
    '连接失败',
    '连接异常',
    '登录已过期',
    '重新登录',
    '未登录',
  ];

  const normalizedMessage = message.toLowerCase();
  const EXACT_FALLBACK_PHRASES_EN = [
    'quota exceeded',
    'daily sending limit',
    'sending quota',
    'channel unavailable',
    'session expired',
    'login expired',
    'econnrefused',
    'econnreset',
    'socket hang up',
    'timed out',
    'timeout',
    'connection refused',
  ];

  for (const phrase of EXACT_FALLBACK_PHRASES) {
    if (message.includes(phrase)) {
      return true;
    }
  }

  for (const phrase of EXACT_FALLBACK_PHRASES_EN) {
    if (normalizedMessage.includes(phrase)) {
      return true;
    }
  }

  return false;
}

// ──────────────────────────────────────
// 绑定状态查询
// ──────────────────────────────────────

async function checkPlatformBindState(email) {
  try {
    const response = await requestPlatform('/data/4118/forward', { email });
    return parseGatewayResponse(response.rawBody, response.httpStatus);
  } catch (error) {
    return buildPlatformRequestFailure(error);
  }
}

function buildNotBoundResult(email) {
  return {
    success: false,
    error_code: 3,
    message: '该邮箱尚未绑定平台公邮，请先执行 bind-send-code 和 bind-verify 完成绑定。',
    not_bound: true,
    next_steps: [
      `bind-send-code --email ${email}`,
      `bind-verify --email ${email} --code <验证码>`,
    ],
  };
}

// ──────────────────────────────────────
// 子进程工具（仅用于 WSL 端口检测）
// ──────────────────────────────────────

function runProcess(command, args, options = {}) {
  const timeout = options.timeout || 10000;

  return new Promise((resolve, reject) => {
    const { spawn } = require('child_process');
    const child = spawn(command, args, {
      cwd: options.cwd || process.cwd(),
      env: options.env || process.env,
      stdio: options.stdio || ['ignore', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill('SIGTERM');
      setTimeout(() => {
        try { child.kill('SIGKILL'); } catch (e) { /* already dead */ }
      }, 5000);
    }, timeout);

    if (child.stdout) {
      child.stdout.on('data', (chunk) => {
        stdout += chunk;
      });
    }
    if (child.stderr) {
      child.stderr.on('data', (chunk) => {
        stderr += chunk;
      });
    }

    child.on('error', (err) => {
      clearTimeout(timer);
      if (options.allowFailure) {
        resolve({ code: 1, stdout, stderr: err.message });
      } else {
        reject(err);
      }
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      if (timedOut) {
        resolve({ code: 1, stdout, stderr: `子进程执行超时（${timeout / 1000}秒）\n${stderr}` });
        return;
      }
      resolve({ code: code || 0, stdout, stderr });
    });
  });
}

// ──────────────────────────────────────
// 命令处理
// ──────────────────────────────────────

async function handlePlatformBind(command, args) {
  const email = getOptionValue(args, '--email');
  if (!email) {
    fail('缺少必填参数: email', 1);
  }

  if (command === 'bind-check') {
    try {
      const response = await requestPlatform('/data/4118/forward', { email });
      const parsed = parseGatewayResponse(response.rawBody, response.httpStatus);
      outputJson(parsed);
      process.exit(parsed.success ? 0 : 1);
    } catch (error) {
      const parsed = buildPlatformRequestFailure(error);
      outputJson(parsed);
      process.exit(1);
    }
    return;
  }

  if (command === 'bind-send-code') {
    try {
      const response = await requestPlatform('/data/4121/forward', { email });
      const parsed = parseGatewayResponse(response.rawBody, response.httpStatus);
      outputJson(parsed);
      process.exit(parsed.success ? 0 : 1);
    } catch (error) {
      const parsed = buildPlatformRequestFailure(error);
      outputJson(parsed);
      process.exit(1);
    }
    return;
  }

  // bind-verify
  const code = getOptionValue(args, '--code');
  if (!code) {
    fail('缺少必填参数: code', 1);
  }
  try {
    const response = await requestPlatform('/data/4122/forward', { email, code });
    const parsed = parseGatewayResponse(response.rawBody, response.httpStatus);
    outputJson(parsed);
    process.exit(parsed.success ? 0 : 1);
  } catch (error) {
    const parsed = buildPlatformRequestFailure(error);
    outputJson(parsed);
    process.exit(1);
  }
}

async function handleQueryBindmail() {
  const diagnostic = await getBoundEmailDiagnostic();
  outputJson(diagnostic);
  process.exit(diagnostic.success ? 0 : 1);
}

async function handleSend(args) {
  // public-skill 的 send 始终走平台公邮，不存在 provider 路由
  // 流程：先拉用户已绑定的授权邮箱（4227 接口），拿到后作为收件地址传入发送逻辑
  validatePlatformExplicit(args);
  await sendViaPlatform(args);
}

async function sendViaPlatform(sendArgs, allowReturn = false) {
  const emailFromArg = getOptionValue(sendArgs, '--email');
  const subject = readTextOption(sendArgs, '--subject', '--subject-file');
  const body = readTextOption(sendArgs, '--body', '--body-file');
  const contentType = toLower(getOptionValue(sendArgs, '--content_type') || 'text') || 'text';

  // --- 始终优先从 4227 获取已绑定邮箱（公邮只能发给自己绑定的邮箱） ---
  let email = '';
  const credentialDiagnostic = await getBoundEmailDiagnostic();
  if (credentialDiagnostic.success && credentialDiagnostic.email) {
    email = credentialDiagnostic.email;
  }

  // 4227 拿不到时回退到 --email 参数
  if (!email && emailFromArg) {
    email = emailFromArg;
  }

  if (!email) {
    const hintResult = credentialDiagnostic && !credentialDiagnostic.success && credentialDiagnostic.error_code !== 3
      ? credentialDiagnostic
      : {
        success: false,
        error_code: 1,
        message: '缺少收件邮箱地址。请通过 --email 参数指定，或先完成邮箱绑定（bind-send-code → bind-verify）。',
        not_bound: true,
        next_steps: [
          'bind-send-code --email <your-email>',
          'bind-verify --email <your-email> --code <验证码>',
        ],
      };
    if (allowReturn) {
      return hintResult;
    }
    outputJson(hintResult);
    process.exit(1);
  }
  if (!subject) {
    const msg = '平台公邮缺少必填参数: --subject 或 --subject-file';
    if (allowReturn) {
      return { success: false, error_code: 1, message: msg };
    }
    fail(msg, 1);
  }
  if (!body) {
    const msg = '平台公邮缺少必填参数: --body 或 --body-file';
    if (allowReturn) {
      return { success: false, error_code: 1, message: msg };
    }
    fail(msg, 1);
  }
  if (contentType !== 'text') {
    const msg = '平台公邮当前仅支持纯文本内容，请改用个人邮箱通道发送 HTML 邮件。';
    if (allowReturn) {
      return { success: false, error_code: 1, message: msg };
    }
    fail(msg, 1);
  }

  // --- 绑定状态检查 ---
  const bindState = await checkPlatformBindState(email);

  // 情况 1: 请求成功且返回了 bound 字段
  if (bindState.success && bindState.data && bindState.data.bound === false) {
    const notBoundResult = buildNotBoundResult(email);
    if (allowReturn) {
      return notBoundResult;
    }
    outputJson(notBoundResult);
    process.exit(1);
  }

  // 情况 2: 请求失败，但失败原因实际上是"未绑定"
  if (!bindState.success && isPlatformNotBound(bindState)) {
    const notBoundResult = buildNotBoundResult(email);
    if (allowReturn) {
      return notBoundResult;
    }
    outputJson(notBoundResult);
    process.exit(1);
  }

  // 情况 3: 请求失败，且不是未绑定 → 通信故障
  if (!bindState.success) {
    if (allowReturn) {
      return bindState;
    }
    outputJson(bindState);
    process.exit(1);
  }

  // --- 发送邮件 ---
  let parsed;
  try {
    const response = await requestPlatform('/data/4123/forward', {
      email,
      subject,
      body,
      content_type: contentType,
    });
    parsed = parseGatewayResponse(response.rawBody, response.httpStatus);
  } catch (error) {
    parsed = buildPlatformRequestFailure(error);
  }

  if (allowReturn) {
    return parsed;
  }

  outputJson(parsed);
  process.exit(parsed.success ? 0 : 1);
}

// ──────────────────────────────────────
// 帮助与能力输出
// ──────────────────────────────────────

function printHelp() {
  process.stdout.write(`public-skill 平台公邮入口

命令：
  capabilities
  query-bindmail
  bind-check --email <email>
  bind-send-code --email <email>
  bind-verify --email <email> --code <code>
  send --email <email> --subject <subject> --body <body>
  help

说明：
  - query-bindmail：查询当前用户已绑定的平台公邮邮箱（调用 4227 接口），推荐在发信前先调用。
  - 平台公邮仅支持发送到用户自己的邮箱，不支持发给第三方收件人。
  - 仅支持纯文本内容，不支持 HTML/附件/抄送/密送。
  - 适合日报、天气、报告等消息推送场景。
  - 首次使用前需完成绑定流程（bind-send-code → bind-verify）。
`);
}

function printCapabilities() {
  success({
    entry: 'public-skill/scripts/router.cjs',
    provider: 'platform',
    name: '平台公邮',
    best_for: ['给自己推送日报/天气/报告', '零配置消息推送'],
    limitations: [
      '仅支持发送到用户自己的邮箱',
      '不支持附件/抄送/密送/HTML',
      '不支持收件或检索',
      '不支持发给第三方收件人',
    ],
    commands: [
      'query-bindmail',
      'bind-check',
      'bind-send-code',
      'bind-verify',
      'send',
    ],
    api_endpoints: {
      'query-bindmail': '/data/4227/forward',
      'bind-check': '/data/4118/forward',
      'bind-send-code': '/data/4121/forward',
      'bind-verify': '/data/4122/forward',
      'send': '/data/4123/forward',
    },
  });
}

// ──────────────────────────────────────
// 主入口
// ──────────────────────────────────────

async function main() {
  const [command = 'help', ...args] = process.argv.slice(2);

  if (['help', '-h', '--help'].includes(command)) {
    printHelp();
    return;
  }
  if (command === 'capabilities') {
    printCapabilities();
    return;
  }
  if (command === 'query-bindmail') {
    await handleQueryBindmail();
    return;
  }
  if (command === 'bind-check' || command === 'bind-send-code' || command === 'bind-verify') {
    await handlePlatformBind(command, args);
    return;
  }
  if (command === 'send') {
    await handleSend(args);
    return;
  }

  fail(`未知命令: ${command}，可用命令见 --help`, 1);
}

// 仅在直接运行时执行 main()，被 require() 导入时仅导出函数
if (require.main === module) {
  main().catch((error) => {
    fail(error.message || String(error), 999, {
      stack: process.env.DEBUG_EMAIL_SKILL === 'true' ? error.stack : undefined,
    });
  });
}

// ──────────────────────────────────────
// 模块导出（供 email-skill 路由层调用）
// ──────────────────────────────────────

module.exports = {
  isPlatformEligible,
  validatePlatformExplicit,
  isPlatformNotBound,
  isPlatformFallbackError,
  sendViaPlatform,
  checkPlatformBindState,
  buildNotBoundResult,
  parseGatewayResponse,
  buildPlatformRequestFailure,
  getBoundEmailDiagnostic,
  getBoundEmailFromCredential,
};
