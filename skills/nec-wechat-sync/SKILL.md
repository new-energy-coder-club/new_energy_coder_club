---
name: nec-wechat-sync
description: |
  同步分析 NEC 战队微信群聊并生成结构化报告，供飞书 openClaw 机器人读取。
  使用场景：
  1. 导出指定微信群聊天记录（markdown/json）和成员列表
  2. 分析群聊内容，输出时间线、组织架构、关键里程碑、活跃度等维度
  3. 生成固定格式的记录文档（.md），放置于 openClaw 可读取的目录
  4. 当用户提及"同步分析微信群聊"、"导出微信记录"、"整理群聊报告"、"NEC-Claw 读取"时触发
---

# NEC WeChat Sync

Sync and analyze WeChat group chats for NEC team, output structured reports for Feishu openClaw bots.

## Prerequisites

- `wechat-cli` installed and initialized (`wechat-cli init`)
- Python 3.10+
- Windows: set `PYTHONIOENCODING=utf-8` before running `wechat-cli`

## Quick Start

### 1. Export Chat History

```bash
python scripts/export_analyze.py export "群名称" --output-dir D:\NEC-Claw\docs\wechat-analysis
```

Outputs:
- `chat_群名.md` — markdown chat history
- `members_群名.json` — member list

### 2. Analyze and Generate Report

```bash
python scripts/export_analyze.py analyze chat_群名.md members_群名.json --output record_群名.md
```

Or let Kimi read the exported markdown and generate the report using the template below.

## Output Format (openClaw-compatible)

Generated records must follow this structure:

```markdown
# 群聊分析记录：{群名}

## 元信息
| 项目 | 内容 |
|------|------|
| 群名 | ... |
| 群ID | ... |
| 群主 | ... |
| 成员数 | ... |
| 消息量 | ... |
| 时间跨度 | ... |
| 导出时间 | ... |
| 分析版本 | v1.0 |

## 成员列表
| 序号 | 昵称 | 备注 | 组别 | 角色 |
|------|------|------|------|------|

## 关键时间线

### 阶段1：...
- date: YYYY-MM-DD
- events: ...

## 高频话题标签
| 标签 | 出现次数 | 关联成员 |
|------|----------|----------|

## 待办/待跟进
- [ ] ...

## 原始文件路径
- 聊天记录: ...
- 成员列表: ...
```

## Default Output Directory

Place final `.md` records at:

```
D:\NEC-Claw\docs\wechat-analysis\
```

This path is monitored by openClaw Feishu bots. Do not change without updating bot config.

## Analysis Dimensions

Always include these sections:
1. **基础信息** — 群名、ID、群主、人数、消息量、时间跨度
2. **组织架构** — 职能分组（机械/电控/视觉/运营/管理）
3. **关键时间线** — 建群→报名→开工→中期→当前状态
4. **内容主题分布** — 快递/加工/行政/技术/运营 占比
5. **高频互动人物** — 核心成员及其角色特征
6. **待关注事项** — 风险、滞后项、下一步行动

## References

- `references/record_26RC参赛群-常州工NEC.md` — Sample record (参赛总群)
- `references/record_26常工院NEC-RC主赛.md` — Sample record (主赛备赛群)
