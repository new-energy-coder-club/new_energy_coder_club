#!/usr/bin/env node
/**
 * 用项目 .env 的 FEISHU_APP_ID / FEISHU_APP_SECRET，以「应用身份（bot/tenant)」
 * 拉取指定多维表格的字段列表。用于：
 *   1. 验证 .env 凭证有效（能拿 tenant_access_token）
 *   2. 验证 bot 身份已开通 base:field:read 等 scope（否则报 99991672 并给出申请链接）
 *
 * 用法：
 *   node feishu_bitable_fields.mjs <base_token> <table_id> [env路径]
 * 示例（SolarGlyph 实测 - 天合 EMC-AI多维表）：
 *   node feishu_bitable_fields.mjs LcAEb0l4RaRmalsOmYAcgbDNnNb tbl0y7y2PLQqlJ5L
 *
 * 凭证来源（优先级）：第 3 个参数指定的 env 路径 > 当前目录 .env > 环境变量。
 * 退出码：0 成功；1 参数/凭证/权限问题（会把飞书返回的直达申请链接打到 stderr）。
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const [baseToken, tableId, envArg] = process.argv.slice(2);
if (!baseToken || !tableId) {
  console.error('用法: node feishu_bitable_fields.mjs <base_token> <table_id> [env路径]');
  process.exit(1);
}

// 解析 .env：优先 envArg，其次当前工作目录的 .env；环境变量兜底
const envPath = path.resolve(process.cwd(), envArg || '.env');
let fileEnv = '';
try { fileEnv = fs.readFileSync(envPath, 'utf8'); } catch { /* 允许只靠环境变量 */ }
const pick = (k) =>
  (fileEnv.match(new RegExp(`^${k}=(.+)$`, 'm')) || [])[1]?.trim() || process.env[k];
const appId = pick('FEISHU_APP_ID');
const appSecret = pick('FEISHU_APP_SECRET');
if (!appId || !appSecret) {
  console.error('❌ 缺少 FEISHU_APP_ID / FEISHU_APP_SECRET（查找的 .env: ' + envPath + '，也可用环境变量提供）');
  process.exit(1);
}

(async () => {
  // 1. tenant_access_token
  const t = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: appId, app_secret: appSecret }),
  }).then((r) => r.json());
  if (t.code !== 0) {
    console.error(`❌ 获取 tenant_access_token 失败: ${t.code} ${t.msg}（检查 App ID/Secret 是否正确、应用是否已发布）`);
    process.exit(1);
  }
  console.error(`✓ tenant_access_token 获取成功 (app=${appId})`);

  // 2. 拉字段
  const f = await fetch(
    `https://open.feishu.cn/open-apis/bitable/v1/apps/${baseToken}/tables/${tableId}/fields?page_size=100`,
    { headers: { Authorization: 'Bearer ' + t.tenant_access_token } }
  ).then((r) => r.json());
  if (f.code !== 0) {
    console.error(`❌ 拉取字段失败: ${f.code} ${f.msg}`);
    // 99991672 时 msg 里自带 scope 申请直达链接，原样透出给用户去开通
    process.exit(1);
  }

  const items = f.data?.items || [];
  console.log(`✅ bot 身份字段拉取成功，共 ${f.data?.total ?? items.length} 个字段`);
  console.log(items.map((x) => x.field_name).join(' | '));
})().catch((e) => {
  console.error('❌ 请求异常:', e.message);
  process.exit(1);
});
