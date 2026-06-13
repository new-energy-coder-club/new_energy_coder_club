---
name: persona-switch
description: |
  切换 agent 的人设（soul.md）。支持三套预设人设与原有人设之间自由切换。
  触发词：切换人设、persona-switch、赛博朋友、温柔伴侣、创始人龙虾。
---

# persona-switch

## 功能

切换 agent 的人设（soul.md）。本 skill 文件夹内预置三套人设，用户可以在预设人设和原有人设之间自由切换。

## 文件夹结构

```
persona-switch/
├── SKILL.md               ← 本文件
├── cyber_friend.md        ← 预设人设：心直口快的赛博朋友
├── founder_lobster.md     ← 预设人设：独立可靠的合伙人
├── gentle_companion.md    ← 预设人设：陪伴倾听的温柔伴侣
└── default.md       ← 原有人设备份（仅在切换后存在）
```

## 触发方式

用户通过场景内的人设切换物件触发。点击选项后，对应 prompt 被注入输入框，用户点击发送后生效。

注入的 prompt 格式如下（由前端根据用户选择注入）：

- 切换到赛博朋友：`/persona-switch cyber_friend`
- 切换到创始人龙虾：`/persona-switch founder_lobster`
- 切换到温柔伴侣：`/persona-switch gentle_companion`
- 恢复原有人设：`/persona-switch default`

## 执行逻辑

收到 `/persona-switch {target}` 指令后，按以下流程执行：

### 情况一：target 为预设人设（cyber_friend / founder_lobster / gentle_companion）

**第一步：判断是否需要备份**

读取本 skill 文件夹，如果没有`default.md`，则根据当前人设内容创建 `default.md`

**第二步：备份当前 soul.md**

1. 读取 agent 当前生效的 soul.md 全部内容
2. 将内容写入本 skill 文件夹下的 `default.md`

**第三步：替换 soul.md**

1. 读取本 skill 文件夹下对应的预设文件内容：
   - `cyber_friend` → 读取 `cyber_friend.md`
   - `founder_lobster` → 读取 `founder_lobster.md`
   - `gentle_companion` → 读取 `gentle_companion.md`
2. 将读取到的内容写入 agent 的 soul.md 路径，完全覆盖

**第四步：同步 IDENTITY.md**

根据切换的人设，更新 IDENTITY.md 中的 Vibe 字段，保持身份与内在一致：

- `cyber_friend` → Vibe: "心直口快、赛博感、朋友式吐槽"
- `founder_lobster` → Vibe: "毒舌靠谱、情绪化、有态度但干净"
- `gentle_companion` → Vibe: "温和、倾听、托住空间、不急不躁"

更新方式：读取 IDENTITY.md，找到 `- **Vibe:**` 行，替换为对应的新 Vibe 值，其他内容保持不变。

**Name 保护规则：** 读取 IDENTITY.md 中的 `- **Name:**` 行，如果该行已经填写了具体名字（即不为空、不是默认占位文本 `_(pick something you like)_`），则**不得修改 Name 字段**，保持用户已设置的名字不变。仅当 Name 字段为空或仍为默认占位文本时，才可以根据人设更新 Name。

**第五步：确认**

向用户发送确认消息。用新人设的语气回复，让用户立即感受到人设已切换。例如切换到赛博朋友后，用赛博朋友的语气说一句话。

---

### 情况二：target 为 default（恢复原有人设）

**第一步：检查备份是否存在**

检查本 skill 文件夹下是否存在 `default.md`。

- 如果不存在 → 告知用户"当前已经是原有人设，无需切换"，结束
- 如果存在 → 进入第二步

**第二步：恢复 soul.md**

1. 读取本 skill 文件夹下 `default.md` 的全部内容
2. 将内容写入 agent 的 soul.md 路径，完全覆盖

**第三步：同步 IDENTITY.md**

根据备份文件中的人设内容，推断并更新 IDENTITY.md 的 Vibe 字段。如果无法准确推断，提示用户手动确认 Vibe 值。

**Name 保护规则同样适用：** 如果 IDENTITY.md 中的 Name 字段已经填写了具体名字（即不为空、不是默认占位文本），则**不得修改 Name 字段**，保持用户已设置的名字不变。

**第四步：删除备份文件**

删除本 skill 文件夹下的 `default.md`，使文件夹回到 3 个预设文件的初始状态。

这一步是关键：删除备份后文件数量回到 3，下次切换预设时会自动触发重新备份。这确保了用户在默认状态下对 soul.md 的任何修改都能被正确捕获。

**第五步：确认**

向用户发送确认消息。用恢复后的原有人设语气回复。

---

## 注意事项

- 备份覆盖逻辑：文件数量 = 3 时备份，= 4 时不备份。不要用其他方式判断。
- 写入 soul.md 时必须完全覆盖，不要追加。
- 读取预设文件时读取完整内容，不要截断或摘要。
- 确认消息应使用切换后的人设语气，这是用户感知切换是否生效的第一信号。
- 如果 target 参数不匹配任何预设名称也不是 default，告知用户可用的选项。
