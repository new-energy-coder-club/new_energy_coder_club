# 开源仓库高效团队协作指南

## 1. 看板列与状态管理 (Status)

我们将 Issue 的生命周期固定为以下 6 个阶段，通过 `status:*` 标签进行管理：

| 状态标签 | 对应看板列 | 含义 |
| :--- | :--- | :--- |
| `status:backlog` | **Backlog** | 需求池 / 暂未排期 (默认状态) |
| `status:todo` | **To do** | 已排期，待开始 (Owner 已确认) |
| `status:doing` | **Doing** | 进行中 |
| `status:review` | **Review** | 待评审 / 待合入 / 待验收 |
| `status:blocked` | **Blocked** | 阻塞中 (必须说明阻塞原因) |
| `status:done` | **Done** | 完成 ✅ |

> **规则**：看板列 = `status` 标签。列的变化即为标签的变化。

---

## 2. Issue 提单规范 (Minimum Requirements)

任何人提交 Issue，必须满足“最小必填”信息，以便快速分诊：

1.  **类型 (Type)**：`bug` / `feature` / `enhancement` / `question` (外部友好)
2.  **优先级 (Priority)**：`prio:P*` (内部管理)
    *   `P0`: 严重阻塞/安全风险 (立刻处理)
    *   `P1`: 本迭代必须完成
    *   `P2`: 重要但可延期
    *   `P3`: 低优先级/优化
3.  **模块 (Module)**：`module:*` (明确归属，如 `VCU`, `BMS`, `Docs` 等)

> **未满足要求的 Issue**：维护者将打上 `team:triage` + `team:owner-needed` 标签，并要求提单人补齐信息。

---

## 3. Triage (分诊) 流程

建议每天或隔天进行一次 10 分钟的快速分诊：

### 1. 处理新 Issue (`team:triage` 或无标签)
*   **补齐标签**：确认 `prio` 和 `module`。
*   **明确 Owner**：指派负责人。如果没有合适人选，打上 `team:owner-needed`。
*   **定状态**：
    *   能做 -> `status:todo`
    *   暂不能做 -> `status:backlog`

### 2. 检查阻塞列 (`status:blocked`)
*   必须同时包含一个 `blocked:*` 标签 (如 `blocked:spec`, `blocked:test-env`)。
*   如果是跨团队问题，追加 `team:cross-team`。
*   **行动**：在评论区说明阻塞点、解除人和预计时间。

### 3. 检查评审列 (`status:review`)
*   **合入/验收** -> 推进至 `status:done`
*   **打回** -> 退回 `status:doing` 并说明缺失内容。

---

## 4. 开发闭环与 Done 标准

一个 Issue 进入 **Done** 必须满足：

1.  标签为 `status:done`。
2.  **Bug 类**：必须包含“如何验证修复有效”的记录。
3.  **线下类**：必须包含 `offline:issue-verified` 标签，或在评论区贴出验证记录/日志时间戳。

> 这样统计出的 Done 才是可信的。

---

## 5. 周报统计 (Weekly Report)

每周固定时间 (如周五) 按标签筛选并生成周报：

1.  **本周完成 (Done)**
    *   筛选：`status:done` + `closed` (本周)
    *   分组：按 `module` 或 `type`
2.  **本周新增 (New)**
    *   筛选：本周新建 (`created` 本周)
    *   关注：`prio:P0/P1` 的新增数量
3.  **下周计划 (Plan)**
    *   筛选：`status:todo` + `status:doing`
    *   排序：按 `prio` 列出 Top N
4.  **阻塞清单 (Blocked)**
    *   筛选：`status:blocked`
    *   输出：阻塞原因 (`blocked:*`) + 预期解除时间

---

## 6. 推荐工作法 (Best Practices)

*   **粒度控制**：每个 Issue 应在 2-3 天内闭环。大需求请拆分。
*   **PR 关联**：PR 描述中必须引用 Issue 编号 (Fixes #xxx)。
*   **新手任务**：
    *   开源社区：使用 `good first issue` / `help wanted`
    *   内部进度：使用 `team:help-needed`
*   **减少争论**：
    *   需要决策时打上 `team:decision`。
    *   决策结论更新在 Issue 顶部 (Description)，避免后来者翻阅长评论。
