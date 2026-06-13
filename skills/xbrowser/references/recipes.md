# xbrowser 真实场景手册

**本文件定位**：给 agent 参考的「怎么把命令串成完整任务」模板。不重复命令语法（见 `xb-browser-commands.md`），只演示真实任务中的命令序列、决策点、失败恢复路径。

**使用方式**：遇到非单步的浏览器任务（登录、爬取、多页操作、batch 失败等）前，先按"场景速查"定位相关章节。

以下所有命令省略 `"$NODE" {baseDir}/scripts/xb.cjs` 前缀，实际执行时必须带上。

---

## 占位符约定（重要：执行前必看）

**示例中的以下符号都是占位符，不要原样写进真实命令**：

| 占位符 | 含义 | 怎么替换 |
|--------|------|---------|
| `@e<N>`（如 `@e1`、`@e3`、`@e12`） | 元素编号 | 必须替换为**本轮 `snapshot -i` 返回 JSON 里的真实编号**。示例里的数字只是示意，不要照抄。 |
| `$LOGIN_USER` / `$LOGIN_PASS` | 登录凭据变量 | 由调用方提供。外层 shell 已 `export` 时可保留写法；否则替换为真实值（但不要把明文凭据写进日志）。 |
| `<URL>`、`<SELECTOR>`、`<PATH>` | 需按任务替换的参数 | 根据实际任务替换为目标 URL / CSS 选择器 / 文件路径。 |
| `# ← ...` 注释 | 提示你当前行需要替换/注意什么 | 不要复制到命令里。 |

**反例**（这些都是错的）：
```bash
xb run --browser default click @e新编号        # ❌ 中文被照搬进命令
xb run --browser default click @e<N>           # ❌ 尖括号被照搬
xb run --browser default fill @e1 "$USER"      # ❌ $USER 是系统当前登录名，不是登录凭据
```

---

## 首选命令速查（决策卡死时看这里）

当你在"多种写法之间犹豫"时，默认选下表的首选。只有首选不适用才考虑备选。

| 场景 | 首选 | 仅当首选失败才考虑 |
|------|------|--------------------|
| 等页面加载完成 | `wait --load networkidle` | `wait <ms>`（固定毫秒，最后手段） |
| 等待跳转到某 URL | `wait --url "**/<path>" --timeout 10000` | `get url` 后自己对比 |
| 等待某段文案出现 | `wait --text "<文本>" --timeout 5000` | - |
| 点击有文字的按钮 | `find role button click --name "<按钮文字>"` | `snapshot -i` → `click @e<N>` |
| 填写有 label 的输入框 | `find label "<label 文字>" fill "<值>"` | `snapshot -i` → `fill @e<N> "<值>"` |
| 连续多条命令（每步都会成功，不需中间分支） | `batch --bail "cmd1" "cmd2" ...` | 顺序执行 |
| 连续多条命令（需要看中间 JSON 决策） | **顺序执行**（一条一条） | 不能用 batch |
| 查 JS 错误 | `errors` | 再看 `console` |

---

## 场景速查

| 你要做的事 | 看哪节 |
|-----------|--------|
| 登录表单 + 验证跳转 | §1 |
| 登录后做后续多页操作 | §2 |
| 爬取列表 / 表格 / 分页数据 | §3 |
| `click @eN` 报"元素引用已失效" | §4 |
| 一次跑多条命令（batch 还是顺序） | §5 |
| 忘了基本节奏（open 之后该干啥） | §0 通用节奏 |

---

## §0. 通用节奏（所有场景共用）

### 规则 1：任何 `click` 或 `open` 之后，必须重做 wait + snapshot

**不要自己判断"这个 click 是不是导航按钮"。一律按下面这三步走**：

```bash
xb run --browser default click @e<N>              # 或 open / back / forward / reload / tab new
xb run --browser default wait --load networkidle  # 等加载
xb run --browser default snapshot -i              # 拿新 @ref
# 后续只能使用这一步返回的新编号，上一次 snapshot 的 @ref 已全部失效
```

唯一的例外：点击之后只是填下一个输入框（`fill @e<M>`），且能确认上一步 click 没引起页面跳转/重渲染（例如点的是纯 UI 的展开箭头）——这种情况不常见，拿不准就按上面三步重做。

### 规则 2：`open` 之后先等加载，再 snapshot

```bash
xb run --browser default open <URL>
xb run --browser default wait --load networkidle   # 首选，不要省略
xb run --browser default snapshot -i
```

不要 `open` 后直接 `snapshot`——大概率拿到半加载状态。

### 规则 3：每条命令返回 JSON，检查 `ok` 再决定下一步

每条 `xb run` 返回 `{ ok, data?, error?, hint? }`：
- `ok=true` → 继续下一条
- `ok=false` → 看 `error` 和 `hint`，按 `hint` 操作（不要盲目重试）

**禁止**：用 `&&`、`&`、`;` 拼接多条 `xb run`（原因见 SKILL.md）。多条命令用 `batch`（见 §5）。

### 规则 4：优先用 `find` 语义定位，减少 snapshot 依赖

**使用 `find` 的判断清单**（按以下顺序检查 snapshot 返回的 JSON，任一命中即用 `find`，无需依赖 `@ref`）：

1. 元素是**按钮**，且按钮上有**可见文字** → `find role button click --name "<按钮文字>"`
2. 输入框前面有 **label 文字** → `find label "<label 文字>" fill "<值>"`
3. 元素有 **可见文本**（链接、菜单项） → `find text "<文本>" click`
4. 元素有 `placeholder` / `aria-label` / `alt` / `data-testid` → 用对应的 `find placeholder/label/alt/testid`
5. 以上都不满足 → 用 `@ref`（仍需要先 `snapshot -i`）

`find` 定位的优势：**不受 DOM 变化影响**。对于翻页按钮、提交按钮、导航菜单这类反复使用的元素，从一开始就用 `find`。

---

## §1. 登录 + 验证跳转

**场景**：用户名/密码表单登录，登录后验证已跳转到目标页面。

**首选路径**：**9 成情况走下面的「方式 A：find 版」**——不需要 snapshot，更稳、更短、@ref 不会失效。只有当登录页的输入框/按钮**完全没有 label/placeholder/可见文字**（罕见）才用「方式 B：@ref 版」。

### 方式 A：find 版（首选）

> 示例里的 `邮箱` / `密码` / `登录` / `/dashboard` 都是**示意文字/路径**，必须按真实页面的 label、按钮文字、登录后路径替换。真实文案可能是 `Email` / `Username` / `Sign in` / `/home` 等。

```bash
# 1. 打开登录页并等待加载
xb run --browser default open https://app.example.com/login
xb run --browser default wait --load networkidle

# 2. 直接用 find 定位，跳过 snapshot
xb run --browser default find label "邮箱" fill "$LOGIN_USER"     # ← "邮箱" 替换为真实 label 文字
xb run --browser default find label "密码" fill "$LOGIN_PASS"     # ← "密码" 替换为真实 label 文字
xb run --browser default find role button click --name "登录"     # ← "登录" 替换为真实按钮文字

# 3. 验证跳转（首选 wait --url）
xb run --browser default wait --url "**/dashboard" --timeout 10000  # ← "**/dashboard" 替换为真实登录后路径
```

**如果不知道真实 label/按钮文字怎么办**：先 `snapshot -i` 看一眼页面结构，从返回 JSON 里读出 label 和按钮的真实文字，再回到 find 命令填入。（不是退化到方式 B——snapshot 只是"侦察"用。）

### 方式 B：@ref 版（备选，仅当元素无语义）

只有在**方式 A 不可行**时用（元素没有 label、按钮没文字只有图标、输入框没 placeholder）：

```bash
# 1. 打开登录页并等待加载
xb run --browser default open https://app.example.com/login
xb run --browser default wait --load networkidle

# 2. 获取可交互元素（返回 JSON 含每个元素的编号 @e1/@e2/...）
xb run --browser default snapshot -i

# 3. 从上一步返回 JSON 中，找到用户名框、密码框、登录按钮的真实编号。
#    下面的 @e1/@e2/@e3 都是示意，不要照抄，用真实编号替换。
xb run --browser default fill @e1 "$LOGIN_USER"   # ← @e1 替换为用户名输入框的真实 @ref
xb run --browser default fill @e2 "$LOGIN_PASS"   # ← @e2 替换为密码输入框的真实 @ref
xb run --browser default click @e3                # ← @e3 替换为登录按钮的真实 @ref

# 4. 验证跳转
xb run --browser default wait --url "**/dashboard" --timeout 10000  # ← 路径按真实替换
```

### 验证登录成功的命令（按优先级，首选即可）

**首选**：`wait --url "**/<目标路径>" --timeout 10000`
→ `ok=true` 说明成功跳转；`ok=false` 超时说明没跳转（登录失败）。

**仅当不知道目标 URL 路径时**：`wait --text "<登录后页面必有的文字>" --timeout 10000`

**最后手段**：`get url` 然后 agent 自己判断返回的 URL 是否匹配预期。

### 失败分支

- `wait --url` 返回 `ok=false` 超时 → 登录失败。执行 `snapshot -i`，查找错误提示元素（JSON 里通常有 role=alert 或显著文字），用 `get text @e<N>` 读取原因。
- 卡在人机验证（验证码/拼图）→ 加 `--headed` 让用户手动完成（见 `authentication.md §3`）。

---

## §2. 登录 + 登录后多页操作

**场景**：登录后需要在 A 页面提交表单，再去 B 页面读取数据。

**核心差异于 §1**：每次页面变化都要重做 `wait + snapshot`——这是 §0 规则 1 的直接应用。

### 完整命令序列

```bash
# ================ 阶段 1: 登录 ================
xb run --browser default open https://app.example.com/login
xb run --browser default wait --load networkidle
xb run --browser default find label "邮箱" fill "$LOGIN_USER"
xb run --browser default find label "密码" fill "$LOGIN_PASS"
xb run --browser default find role button click --name "登录"
xb run --browser default wait --url "**/dashboard" --timeout 10000

# ================ 阶段 2: 导航到 A 页面 ================
# 重要：上一阶段的所有 @ref 已失效。这里必须重新 snapshot。
xb run --browser default open https://app.example.com/settings
xb run --browser default wait --load networkidle
xb run --browser default snapshot -i              # ← 新页面新 @ref
# @e5/@e8 都是示意，从本次 snapshot 返回找真实编号
xb run --browser default fill @e5 "<new value>"   # ← 替换为目标输入框真实 @ref
xb run --browser default click @e8                # ← 替换为提交按钮真实 @ref
xb run --browser default wait --text "保存成功" --timeout 5000

# ================ 阶段 3: 导航到 B 页面 ================
# 又一次页面切换，再次 snapshot
xb run --browser default open https://app.example.com/reports
xb run --browser default wait --load networkidle
xb run --browser default snapshot -i              # ← 又一次新 @ref
xb run --browser default get text @e12            # ← 替换为目标数据元素真实 @ref
```

### 关键模式

- **每次 `open` 或 `click` 跳转后，重复"wait → snapshot → 用新 @ref"三步**（§0 规则 1）。
- **每个阶段之间顺序执行**（不能全部塞进一个 batch），因为要根据上一阶段结果决定下一步。
- **阶段内部可以考虑 batch**：例如阶段 2 的 `fill/click/wait` 如果 @ref 已确定、每步必然成功，可打包成 `batch --bail`（见 §5）。

---

## §3. 分页表格爬取

**场景**：爬取多页表格/列表数据（新闻、商品、搜索结果）。

### 第 0 步（必做）：先看页面结构，再决定选择器

**不要直接照抄下面示例里的 `table tbody tr` 和 `.title` 选择器**——真实页面选择器必须根据实际 DOM 判断。

```bash
xb run --browser default open <URL>
xb run --browser default wait --load networkidle
xb run --browser default snapshot -i -c           # -c 紧凑模式
# 读 snapshot 返回的 JSON，确认：
#   - 列表/表格的容器选择器（如 "table tbody"、"ul.items"、"div.result-list"）
#   - 单行的选择器（如 "tr"、"li"、"div.item"）
#   - 每行内字段的选择器（如 ".title"、"h3"、"a.name"）
# 以下示例选择器都是示意，根据上面结果替换
```

### 模式 A：`eval` 批量提取（推荐，高效）

适合**结构稳定**的表格/列表——一次 `eval` 拿到整页数据：

```bash
# 1. 确认当前页行数（便于后面对比翻页是否成功）
xb run --browser default get count "<ROW_SELECTOR>"   # ← 如 "table tbody tr"

# 2. 批量提取当前页数据
xb run --browser default eval "Array.from(document.querySelectorAll('<ROW_SELECTOR>')).map(r => ({title: r.querySelector('<TITLE_SELECTOR>')?.textContent?.trim(), href: r.querySelector('a')?.href}))"

# 3. 翻页：优先用 find（按钮文字稳定，@ref 会失效）
xb run --browser default find role button click --name "下一页"
xb run --browser default wait --load networkidle

# 4. 再次提取（重复步骤 2-3）
xb run --browser default eval "Array.from(document.querySelectorAll('<ROW_SELECTOR>')).map(r => ({title: r.querySelector('<TITLE_SELECTOR>')?.textContent?.trim(), href: r.querySelector('a')?.href}))"
xb run --browser default find role button click --name "下一页"
xb run --browser default wait --load networkidle

# ... 直到 find 返回 ok=false 或判定到末页（见下方"末页判断"）
```

**关于 eval 的参数引号**：`eval` 的表达式整体用**外层双引号**包住，内部 DOM 选择器用**单引号**。不要在外层同时用单引号否则会和 `xb run` 参数解析冲突。

### 模式 B：`snapshot` + 逐个 `get text`（选择器不好写时的回退）

只在模式 A 写不出稳定选择器时用：

```bash
xb run --browser default snapshot -i -c
# snapshot 返回 JSON 里每一行元素都有独立 @ref。
# 假设返回了 10 行，对应 @e15 到 @e24。逐个提取：
xb run --browser default get text @e15   # ← 真实编号从 snapshot 返回找
xb run --browser default get text @e16
xb run --browser default get text @e17
# ...继续直到处理完所有行（行数以 get count 或 snapshot 返回的元素数量为准）
```

### 末页判断（明确规则，不再"或"）

**按顺序检查，命中任一即判定到达末页，停止循环**：

1. 点击"下一页"前先 `get url` 记下当前 URL；点击后 `wait --load networkidle` 然后再 `get url`。若**两次 URL 相同** → 已到末页。
2. `find role button click --name "下一页"` 直接返回 `ok=false` → 再看 error：若是 "not found"（按钮不存在）则确认末页；若是其他错误（超时/被遮挡）按故障排查处理。
3. 翻页后 `get count "<ROW_SELECTOR>"` 返回行数明显 < 上一页（或为 0）→ 确认末页。

### 防踩坑

- **不要** 每次翻页都 `snapshot -i`——慢且 token 消耗大。翻页用 `find role/text` 定位按钮。
- **必须** 每次翻页后 `wait --load networkidle`，否则抓到上一页的数据。
- **循环次数** 建议设上限（如最多 100 页），防止死循环。

---

## §4. @ref 失效的恢复模式

**症状**：`click @e<N>` / `fill @e<N>` 返回 `ok=false`，`error` 含 "元素引用已失效" 或 "not found"。

**根因**：上一次 `snapshot` 之后 DOM 变了（提交、路由切换、AJAX、动画），`@ref` 编号对应不上。

### 决策流程（按顺序检查）

**问题 1**：在上一次 `snapshot` 返回的 JSON 里，这个元素是否有以下任一字段？
- `name` / `aria-label` / `role` 为 button/link/textbox 等
- 关联的 `label` 文字
- `placeholder` / `alt` / `data-testid`

**如果有** → 改用 `find`，从此不再依赖这个 @ref：

```bash
# ❌ 失败
xb run --browser default click @e8
# → { ok: false, error: "元素引用已失效" }

# ✅ 恢复：改用语义定位
xb run --browser default find role button click --name "提交"
```

**如果没有**（纯 div、没有稳定标签） → 重新 snapshot，用新编号：

```bash
# ❌ 失败
xb run --browser default click @e8
# → { ok: false, error: "元素引用已失效" }

# ✅ 恢复：重新 snapshot + 新编号
xb run --browser default snapshot -i
# 从返回 JSON 找到目标元素的新编号，例如这次叫 @e12
xb run --browser default click @e12           # ← 使用本次 snapshot 返回的真实编号
```

**最多重试 2 次**。两次都失败 → 见下方"还是失败？"清单。

### 防止 @ref 失效的习惯

1. **snapshot 必须紧挨使用点**：snapshot 和使用该 @ref 的命令之间，**不允许插入任何其他 `xb run` 命令**（`wait` 除外）。如果中间必须插入其他命令，使用前必须重做 snapshot。
2. **阶段内部用 batch 包装**（见 §5）：batch 执行期间 DOM 基本稳定，降低失效概率。
3. **可语义描述的元素一开始就用 `find`**：翻页、登录、导航、提交按钮——不要依赖 @ref。

### 还是失败？检查以下特殊情况

| 检查项 | 命令 | 怎么办 |
|--------|------|--------|
| 元素在 iframe 里 | snapshot 返回 JSON 里看到 `iframe` 节点 | 先 `frame "<iframe selector>"` 切入再 snapshot |
| 元素不可见 | `is visible @e<N>` 返回 false | 先 `scrollintoview @e<N>` 再 click |
| 有 dialog 挡住 | `dialog status` 返回有 dialog | 先 `dialog accept` 或 `dialog dismiss` |
| 元素被 disabled | `is enabled @e<N>` 返回 false | 检查业务状态（表单字段是否缺失） |

---

## §5. batch 命令：何时用、怎么处理失败

**前提**：禁用 `&&`/`&`/`;` 拼接 xb 命令。需要连续执行多条命令时，用 `xb run batch`。

### 决策表（三选一）

| 你的情况 | 选择 | 原因 |
|---------|------|------|
| 一连串命令都**不需要看中间 JSON 就能确定怎么写**（如 open → wait → snapshot） | `batch --bail` | 减少进程启动开销；首条失败自动停 |
| 下一步命令的参数**依赖上一步 JSON**（如 snapshot 返回后才知道 @ref） | **顺序执行**（一条一条） | batch 内部无法把上一条结果带入下一条 |
| 批量做同类操作，**允许部分失败继续**（如爬 100 行，失败几行能接受） | `batch`（不加 `--bail`） | 失败继续，最后统一看哪几条失败 |
| 拿不准 | **默认顺序执行** | 更容易排查 |

### 模式 A：确定性链路用 `batch --bail`

```bash
xb run --browser default batch --bail \
  "open https://example.com/login" \
  "wait --load networkidle" \
  "snapshot -i"
```

首条失败 → 后续不再执行，直接返回。

### 模式 A+：batch 条目内部含引号参数（高频踩坑点）

当 batch 的条目内部本身需要带引号参数（如 `find label "邮箱" fill "xxx"`），引号会嵌套两层：**外层用双引号包整条 batch 条目，内部引号用反斜杠转义为 `\"`**。

**模板**：用 `find` 做无需 snapshot 的一体化登录：

```bash
xb run --browser default batch --bail \
  "open https://app.example.com/login" \
  "wait --load networkidle" \
  "find label \"邮箱\" fill \"$LOGIN_USER\"" \
  "find label \"密码\" fill \"$LOGIN_PASS\"" \
  "find role button click --name \"登录\"" \
  "wait --url \"**/dashboard\" --timeout 10000"
```

**关键规则**：
1. 每一条 batch 条目外层用 `"..."` 包住（传给 `batch` 的参数）
2. 条目内部如果原本要用 `"abc"`，改写为 `\"abc\"`
3. `$LOGIN_USER` 这类变量**保留**在双引号内——zsh/bash 会在外层双引号里正常展开变量
4. 条目内部**不要用单引号**（会和外层配合出歧义）

**什么时候该用 batch 条目内含引号**：
- 全部走 `find`（没有 @ref 依赖）、参数都确定 → 适合
- 只要有一步参数依赖前一步 JSON（如 `@ref` 要从 snapshot 读）→ 不要用 batch，走**模式 B** 顺序执行

**引号写错的典型错误**：
```bash
# ❌ 错：外层内层都用双引号，没转义 → shell 提前截断
# xb run ... batch --bail "find label "邮箱" fill "$LOGIN_USER""
# ❌ 错：用单引号包外层 → $LOGIN_USER 不会被展开，会原样传入
# xb run ... batch --bail 'find label "邮箱" fill "$LOGIN_USER"'
# ✅ 对：外双内转义
xb run --browser default batch --bail "find label \"邮箱\" fill \"$LOGIN_USER\""
```

### 模式 B：需要分支决策时，顺序执行

```bash
# snapshot 必须单独执行——因为下面 fill/click 的 @ref 要从它的返回 JSON 里读
xb run --browser default snapshot -i
# 读完 snapshot 返回，确认用户名输入框真实编号（假设是 @e3）
xb run --browser default fill @e3 "$LOGIN_USER"   # ← 用 snapshot 返回里的真实编号替换

# 提交后根据 get url 判断分支
xb run --browser default click @e5                # ← 替换为登录按钮真实编号
xb run --browser default wait --load networkidle
xb run --browser default get url
# agent 检查 get url 返回：
#   - 含 /dashboard → 登录成功，进入后续阶段
#   - 仍在 /login → 失败，去 snapshot 看错误提示
```

### 模式 C：容错批量用不带 `--bail` 的 batch

```bash
# 对已知 10 个 @ref，批量点击并提取文本。哪个失败就记录跳过。
xb run --browser default batch \
  "click @e10" "get text @e50" \
  "click @e11" "get text @e51" \
  "click @e12" "get text @e52"
# ↑ 这 6 条命令使用的 @ref 必须都来自同一次 snapshot，且期间页面不会重渲染
```

### batch 失败后怎么解读返回 JSON

> **注意**：以下字段名需要以 `xb.cjs` 实际输出为准。若与真实返回字段不符，以真实字段为准。

batch 的返回 JSON 大致形如：

```json
{
  "ok": false,
  "data": {
    "results": [
      { "command": "open https://...", "ok": true },
      { "command": "wait --load networkidle", "ok": true },
      { "command": "click @e5", "ok": false, "error": "元素引用已失效" }
    ]
  }
}
```

**处理步骤**：
1. 在 `data.results` 数组里找第一条 `ok=false` 的条目
2. 读它的 `error` 和（若有）`hint`
3. 按对应场景处理（@ref 失效 → §4；超时 → `troubleshooting.md`）

### 反面教材对照（不要照抄 ❌ 这部分）

```bash
# ❌ 错：用 && 拼接（以下整行都不要执行）
# xb run --browser default open https://x.com && xb run --browser default snapshot -i

# ❌ 错：把"需要看中间结果"的流程塞进 batch（@e3 拿不到）
# xb run --browser default batch --bail \
#   "snapshot -i" \
#   "fill @e3 '...'"

# ✅ 对：snapshot 单独跑，读取返回后再 fill
xb run --browser default snapshot -i
# agent 读 snapshot 返回 JSON 确认填哪个 ref（如 @e3）
xb run --browser default fill @e3 "..."
```

---

## 附录：跨场景小事故速查

| 事故 | 最可能的原因 | 首选尝试 |
|------|-------------|---------|
| `open` 超时 | 网络慢 / 页面重 | 加 `--timeout 29000`；再 `get url` 看是否部分加载 |
| `snapshot -i` 返回元素异常少 | 页面还没加载完 | 补一次 `wait --load networkidle` 再 snapshot |
| `click` 执行成功但页面没反应 | 元素不在视口 | `scrollintoview @e<N>` 后重试 click |
| 无法操作 iframe 内元素 | 没切入 frame | `frame "<iframe selector>"` 切换后再 snapshot |
| 提交后页面白屏 | JS 报错 | 首选 `errors`；无结果再看 `console` |
| 登录态莫名丢失 | 用错浏览器 | 确认 `--browser` 和之前登录时使用的值一致 |

更多见 `troubleshooting.md`。
