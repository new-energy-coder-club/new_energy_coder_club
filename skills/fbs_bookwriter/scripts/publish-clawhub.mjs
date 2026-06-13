#!/usr/bin/env node
/**
 * 将 OpenClaw 技能目录发布到 ClawHub（https://clawhub.ai）。
 * 前置：已在本机执行 `npx clawhub@latest login`（或 `clawhub login --no-browser --token <API token>`）。
 *
 * 默认技能根：仓库内 openclaw-github-publish（与 `npm run pack:openclaw` 产出一致，需先打包同步该目录）。
 * 覆盖：环境变量 FBS_CLAWHUB_SKILL_ROOT=绝对路径
 *
 * 可选：FBS_CLAWHUB_CHANGELOG、FBS_CLAWHUB_TAGS（逗号分隔，默认含 latest）
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

let skillRoot = process.env.FBS_CLAWHUB_SKILL_ROOT
  ? path.resolve(process.env.FBS_CLAWHUB_SKILL_ROOT)
  : null;

if (!skillRoot) {
  const devMirror = path.join(ROOT, 'openclaw-github-publish');
  if (fs.existsSync(path.join(devMirror, 'SKILL.md'))) {
    skillRoot = devMirror;
  } else if (fs.existsSync(path.join(ROOT, 'SKILL.md'))) {
    skillRoot = ROOT;
  }
}

if (!skillRoot || !fs.existsSync(path.join(skillRoot, 'SKILL.md'))) {
  console.error(
    '[publish-clawhub] 未找到 SKILL.md。主仓请先 npm run pack:openclaw 并同步 openclaw-github-publish；或设置 FBS_CLAWHUB_SKILL_ROOT=技能根目录。',
  );
  process.exit(1);
}

const pkg = JSON.parse(fs.readFileSync(path.join(skillRoot, 'package.json'), 'utf8'));
const version = pkg.version;
const changelog = process.env.FBS_CLAWHUB_CHANGELOG || `OpenClaw 通道 v${version}`;
const tags = process.env.FBS_CLAWHUB_TAGS || 'latest,writing,book,openclaw,fbs,manuscript,longform';

/** ClawHub CLI 在 Windows 上需可解析的目录路径（使用 / 与引号） */
const pathArg = path.resolve(skillRoot).replace(/\\/g, '/');

const quote = (s) => `"${String(s).replace(/"/g, '\\"')}"`;
const cmd = [
  'npx',
  'clawhub@latest',
  'publish',
  quote(pathArg),
  '--slug',
  'fbs-bookwriter',
  '--name',
  quote('FBS-BookWriter'),
  '--version',
  quote(version),
  '--changelog',
  quote(changelog),
  '--tags',
  quote(tags),
].join(' ');

execSync(cmd, { stdio: 'inherit', cwd: ROOT, shell: true });
