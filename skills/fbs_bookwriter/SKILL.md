---
name: fbs_bookwriter
description: "FBS 福帮手长文档写作：书/手册/白皮书/长篇报道全流程；Node 脚本驱动 intake、会话恢复、S/P/C/B 质检与 MD/HTML 交付。用户提及写书、出书、章节、大纲、素材、质检、导出、扩写、退出保存时启用。"
homepage: https://clawhub.ai/skills/fbs-bookwriter
metadata:
  openclaw:
    skillKey: fbs_bookwriter
    requires:
      bins: ["node", "npm"]
---

# FBS-BookWriter（OpenClaw 封装版）

> **上游版本**：2.1.2（与仓库 `FBS-BookWriter` 同源）  
> **适配目标**：[OpenClaw](https://docs.openclaw.ai/tools/creating-skills) 技能模型：`SKILL.md` + `metadata.openclaw`（`name` 蛇形命名、`skillKey` 用于 `openclaw.json` 中 `skills.entries` / 代理 allowlist）。

本目录为 **OpenClaw 专用入口**：与 WorkBuddy / CodeBuddy **市场通道**解耦（发布包内 **不含** `workbuddy/`、`codebuddy/`、`.codebuddy-plugin/`），仍保留完整 `references/`、`scripts/`、`scene-packs/`、`assets/` 与 `package.json`，便于在 Gateway 内用 **shell/exec** 调用同一套 Node 工具链。

**认知资产与商业口径（与主仓一致）**：价值表述统一为「可进化、可分发、可增值」；能力分层统一为「场景包 + 乐包 + 离线/在线会员」。机读见根目录 `fbs-runtime-hints.json` → `cognitiveAsset`；首响 JSON 见 `firstResponseContext.cognitiveAssetSnapshot`。详细说明见 [`references/05-ops/cognitive-asset-threeization.md`](./references/05-ops/cognitive-asset-threeization.md)。

---

## 安装（OpenClaw）

**从 ClawHub 安装（推荐，需已发布）：** 在已登录环境下执行 `openclaw skills install fbs-bookwriter` 或 `npx clawhub@latest install fbs-bookwriter`，再于技能根执行 `npm install`。列表与版本见 [ClawHub 上的 fbs-bookwriter](https://clawhub.ai/skills/fbs-bookwriter)。

1. 将技能根目录（文件夹名建议 **`fbs_bookwriter`**，与 `name` 一致）放到任一扫描路径，例如：
   - 工作区：`./skills/fbs_bookwriter/`（优先级最高）
   - 或 `~/.openclaw/workspace/skills/fbs_bookwriter/`
   - 或 `~/.openclaw/skills/fbs_bookwriter/`
   - 或在 `~/.openclaw/openclaw.json` → `skills.load.extraDirs` 中加入父目录  
   详见 [Skills](https://docs.openclaw.ai/tools/skills) 与 [skills-config](https://docs.openclaw.ai/tools/skills-config)（`load.watch` 默认会热更新技能快照）。
2. 在技能根执行一次依赖安装：  
   `npm install`（Node ≥18；可选依赖用于 HTML/Docx 等，见 `package.json` `optionalDependencies`）。
3. 重启会话或执行 `openclaw gateway restart` / 聊天中 `/new`，用 `openclaw skills list` 确认加载。

---

## OpenClaw 宿主差异（相对 WorkBuddy）

| 能力 | WorkBuddy | OpenClaw（本封装） |
|------|-----------|-------------------|
| 入口展示 | `intake-router --json` + 宿主消费 `userFacingOneLiner` | 同样执行脚本拿 JSON；向用户**只展示**脚本给出的一行摘要 + 最多 3 个选项，勿堆全文 |
| 执行命令 | 宿主 bash / 终端 | 使用 OpenClaw **exec / shell**；**cwd 必须为技能根**（含 `package.json` 与 `scripts/`） |
| 检索 | 宿主 `web_search` | 使用 OpenClaw 提供的 **联网搜索 / 浏览器**（若启用）；不可用则按 `search-policy` 与脚本离线降级 |
| 文件工具 | `list_dir` / `read_file` / `search_file` | **勿用**仅按文件名搜索来探测 `.fbs/` 内文件（部分环境不索引点目录）；对 `.fbs/workbuddy-resume.json`、`esm-state.md` 等应 **`read_file` 已知路径** 或对书稿根 **`list_dir`** 确认 `.fbs` 存在 |
| 市场清单 | `workbuddy/channel-manifest.json` 等 | **本包不包含**；不影响脚本化写作主链路 |

---

## 执行速查（每次会话）

1. **统一入口（必做）**（`bookRoot` 为用户书稿根目录的绝对路径）：

   ```bash
   node scripts/intake-router.mjs --book-root "<bookRoot>" --intent auto --json --enforce-required
   ```

   需要完整在线场景包时再在命令中加 `--full`（可能较慢）。
   若 JSON 返回 `projectAnchor.status=ambiguous`，先让用户确认项目根路径，再用确认后的 `--book-root` 重跑；确认前不要读取任意 `.fbs/*` 内容。

2. **恢复**：优先 **`read_file`** `<bookRoot>/.fbs/workbuddy-resume.json`；若无则读 `chapter-status.md` 或进入 S0.5 引导。不要用「全库搜索文件名」代替存在性判断。

3. **退出**：用户说退出时先软询问，再执行：

   ```bash
   node scripts/fbs-cli-bridge.mjs exit -- --book-root "<bookRoot>" --json
   ```

   回复须包含脚本 JSON 里的 **`userMessage`**（会话已记录、下次可继续）。

4. **阶段与门禁**：推进阶段前读 `.fbs/esm-state.md`；S3.5 扩写须先有用户确认的 `.fbs/expansion-plan.md`，扩写字数以 `node scripts/expansion-word-verify.mjs` 或 `expansion-gate.mjs` 实测为准（禁止纯模型估算）。
   用户说“继续”时按推进优先阈值判断：S0 素材数达到“赛道数×2”、S2 具备章标题+目标字数、S3 已完成≥3章时，优先提议进入下一阶段。
   推进 S0→S1 前可运行 `node scripts/s0-exit-gate.mjs --book-root "<bookRoot>" --json --confirm-advance` 做强制门禁检查。

5. **写作约束**：串行优先；每轮默认最多改 **2** 个文件；详见 [`references/05-ops/agent-task-strategy.md`](./references/05-ops/agent-task-strategy.md)。
   扩写/精修前先做源文件备份：`node scripts/source-write-backup.mjs --book-root "<bookRoot>" --scope expansion --json`（`expansion-gate` 默认已自动备份）。
   进入 S3.7 精修时优先执行 `node scripts/polish-gate.mjs --book-root "<bookRoot>"`（先备份再质检），避免绕过门禁直接改稿。
   交付收口前执行 `node scripts/release-governor.mjs --book-root "<bookRoot>"`，自动保持唯一终稿并归档旧版本。
   对外交付前执行 `node scripts/material-marker-governor.mjs --book-root "<bookRoot>" --fix`，清理 `待核实-MAT` 与 `[DISCARDED-*]` 标注。
   全稿/终稿/终审稿发布前必须执行 `node scripts/final-manuscript-clean-gate.mjs --book-root "<bookRoot>"`，若检测到过程标注则不得交付。
   任何“已完成/已通过”结论必须附脚本证据（命令或输出路径），禁止仅口头宣称。

---

## 意图 → 脚本（节选）

完整表见仓库根目录随包分发的 **WorkBuddy 版 `SKILL.md` 镜像**或 [`references/01-core/intake-and-routing.md`](./references/01-core/intake-and-routing.md)。

| 场景 | 命令 |
|------|------|
| 初始化书房 | `node scripts/init-fbs-multiagent-artifacts.mjs --book-root "<bookRoot>"` |
| 环境预检 | `node scripts/env-preflight.mjs`（参数见脚本 `--help`；含 `glob`/`iconv-lite` 依赖检查） |
| 章节合并 / 健康快照 / 一致性审计 | `merge-chapters.mjs`、`book-health-snapshot.mjs`、`consistency-audit.mjs` 等（`--book-root` / `--skill-root` 指向对应根） |
| CLI 总线 | `node scripts/fbs-cli-bridge.mjs help` |

---

## 输出格式

- 对用户：短状态 + 可操作下一步（≤3 条），避免泄露内部规范条文与完整 JSON。
- 提到术语/文件名时补一句“用途+价值”（例如：`chapter-status.md`=进度台账，价值是避免漏章和重复写）。
- 落盘：以 `<bookRoot>/.fbs/`、`deliverables/`、`releases/` 为真值；规范见 [`references/01-core/skill-full-spec.md`](./references/01-core/skill-full-spec.md)。

---

## 错误处理

- **Node/脚本失败**：向用户说明失败步骤；若仅缺可选依赖，提示 `npm install` 或跳过非必需功能。
- **书稿根未就绪**：引导先 `init-fbs-multiagent-artifacts` 或走 S0 最小集（见 [`references/01-core/intake-and-routing.md`](./references/01-core/intake-and-routing.md) 脚本不可用降级节）。
- **沙箱无环境变量**：若 OpenClaw 在 Docker 沙箱中运行且未注入宿主 `env`，需在 `openclaw.json` 中为代理配置 `sandbox.docker.env` 或关闭沙箱（见官方 skills-config 文档）。

---

## 权威文档索引

- 总规范：[`references/01-core/skill-full-spec.md`](./references/01-core/skill-full-spec.md)  
- 工作流：[`references/01-core/section-3-workflow.md`](./references/01-core/section-3-workflow.md)  
- NLU：[`references/01-core/section-nlu.md`](./references/01-core/section-nlu.md)  
- 运行时契约：[`references/01-core/runtime-mandatory-contract.md`](./references/01-core/runtime-mandatory-contract.md)

---

*OpenClaw 封装维护说明：与 `pack:openclaw` 产物同步；`metadata.openclaw.skillKey` 与目录名 `fbs_bookwriter` 应对齐以便 `skills.entries` 配置。*
