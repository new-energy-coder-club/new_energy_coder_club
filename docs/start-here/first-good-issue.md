# First Good Issue：小白看这里（NEC 任务系统）

> 你不需要“很强”才能贡献。你只需要 **从一个标准的小任务**开始。

---

## 什么是 `good first issue`

满足以下条件的任务，才配叫 `good first issue`：

- ✅ 2 小时以内可完成（新人）
- ✅ 交付标准明确（做完什么算完成）
- ✅ 不需要深上下文（不懂也能按步骤做）
- ✅ 有参考路径（链接到相关文档/文件位置）
- ✅ 不依赖昂贵硬件（最好能本地/仿真完成）

---

## 新人领取任务的标准流程（必看）

### 1) 在 Issues 里筛选
优先找带这些标签的：
- `good first issue`
- `mentor available`（有带教）
- `type:docs`（最稳）

### 2) 认领（避免重复劳动）
在 Issue 下评论一句：
> 我想认领这个任务，我预计在 X 天内提交 PR。

维护者会：
- 给你 `status:in progress`
- 或把你 assign（如平台支持）

### 3) 开分支
分支建议命名：
- `gfi/<issue-id>-short-title`

### 4) 提早开 PR（推荐 Draft PR）
你可以先开一个 Draft PR，把进度贴上来，维护者更容易带你。

### 5) PR 必须包含什么
- 关联 Issue（写 “Fix #xxx” 或者贴链接）
- 简短说明你做了什么
- 本地验证说明（至少写：我跑通了哪个 Demo/检查了哪些文档链接）

---

## NEC 的 `good first issue` 交付标准（统一验收口径）

### 文档类（type:docs）
- ✅ 链接可用（不要 404）
- ✅ 结构清晰（标题/步骤/下一步）
- ✅ 关键步骤可复制运行（命令、路径、输出）
- ✅ 增加了 FAQ/排查（至少 1 条）

### 代码类（type:feature/type:bug）
- ✅ 有最小复现/最小验证
- ✅ 不破坏现有 Demo（至少跑通 `docs/nec-quickstart`）
- ✅ PR 描述里写清楚“怎么验证”

---

## 新手任务清单（你们可以立刻发成 Issues）

> 下面这些建议你们直接复制成 Issue 标题发出去，并打标 `good first issue`。

### A. 文档类（最推荐）
1. **docs：修正文档常见拼写**（Linux / Founder / EDA / maintainer 等）
   - 标签：`good first issue` `type:docs` `difficulty:1` `area:repo`
   - 验收：全文搜索替换并确认语义正确

2. **docs：把“资料链接表格”整理成 Reference 页面**
   - 标签：`good first issue` `type:docs` `difficulty:2` `area:community`
   - 验收：按“机械/硬件/软件/运营”分类；保留提取码/解压码；加“版权与合规声明”

3. **docs：补齐《新人 60 分钟上手》的 Windows/macOS 指南**
   - 标签：`good first issue` `type:docs` `difficulty:1` `area:repo`
   - 验收：每个平台至少一套可复制命令

4. **docs：为 MicroROS(ESP32)Robot 写 1 页“快速开始索引”**
   - 标签：`good first issue` `type:docs` `difficulty:2` `area:ros`
   - 验收：写清楚“需要什么硬件/软件/预估时间/常见坑”

### B. 仓库维护类（适合愿意学 Git 的新人）
5. **repo：为 docs/nec-quickstart 增加一个 `--help` 示例截图**
   - 标签：`good first issue` `type:docs` `difficulty:1` `area:repo`

6. **repo：补一个 PR 模板里的检查项（比如运行 demo 的 checkbox）**
   - 标签：`good first issue` `type:ops` `difficulty:1` `area:repo`

### C. 轻量代码类（新人可尝试）
7. **demo：给 hello_nec.py 增加 `--plot ascii`/`--plot off` 开关**
   - 标签：`good first issue` `type:feature` `difficulty:2` `area:repo`
   - 验收：默认行为不变；新增参数可用

---

## 新人提问方式（能加速解决问题）

复制这个模板发群里/发 Issue：

- 我在跑：`xxx`（贴命令）
- 我的环境：Windows/macOS/Linux + Python 版本
- 我看到的报错：粘贴完整报错（不要只截一行）
- 我已经尝试过：1) xxx 2) xxx
