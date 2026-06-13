# xb run 命令参考

所有浏览器操作通过 `xb run <command>` 执行。每个命令返回 JSON：`{ ok, command, data?, error?, hint?, warnings? }`。

元素引用使用 `@ref` 格式（由 `snapshot` 返回的编号），如 `@e3`。

## 全局选项

以下选项可与任意 `xb run` 命令组合使用：

| 选项 | 说明 |
|------|------|
| `--browser <id>` | 指定浏览器：`cft`（默认）、`chrome`、`edge`、`qqbrowser` |
| `--headed` | 显示浏览器窗口（调试、人机验证） |
| `--timeout <ms>` | 命令超时（毫秒），默认 25000，上限 29000 |

```bash
xb run --browser edge --headed open https://example.com
xb run --timeout 29000 open https://slow-site.com
```

---

## 1. Navigation — 页面导航

```bash
xb run open <url>          # 打开 URL，等待加载完成
xb run back                # 后退
xb run forward             # 前进
xb run reload              # 重新加载
xb run close               # 关闭当前标签页
```

```bash
xb run open https://example.com
xb run open 'https://example.com?q=hello&lang=zh'   # 特殊字符用单引号
```

---

## 2. Snapshot — 页面快照

```bash
xb run snapshot [flags]
```

获取页面可访问性树快照，返回带编号的元素列表。理解页面结构的核心命令。

| 标志 | 说明 |
|------|------|
| `-i` | 仅显示可交互元素（按钮、链接、输入框等） |
| `-c` | 紧凑模式，省略空文本和装饰性元素 |
| `-d <depth>` | 限制树的最大深度 |
| `-s <selector>` | 仅快照匹配选择器的子树 |

```bash
xb run snapshot -i
xb run snapshot -i -c
xb run snapshot -d 3 -s "#main-content"
```

---

## 3. Interaction — 元素交互

```bash
xb run click @ref                   # 单击元素
xb run dblclick @ref                # 双击元素
xb run fill @ref "text"             # 清空后填入文本（适用于 input/textarea）
xb run type @ref "text"             # 逐字符输入（不清空已有内容）
xb run press <key>                  # 按键，支持组合键如 Control+A
xb run hover @ref                   # 悬停
xb run check @ref                   # 勾选复选框/单选按钮
xb run uncheck @ref                 # 取消勾选
xb run select @ref "value"          # 下拉框选值
xb run scroll <dir> [px]            # 滚动：up/down/left/right，可选像素数
xb run scrollintoview @ref          # 滚动元素到可视区
xb run drag @src @dst               # 拖拽元素
xb run upload @ref <file>           # 文件上传
xb run focus @ref                   # 设置焦点
xb run keydown <key>                # 按下按键
xb run keyup <key>                  # 释放按键
```

```bash
xb run fill @e7 "hello@example.com"
xb run press Enter
xb run press Shift+Tab
xb run scroll down 300
xb run drag @e5 @e18
xb run upload @e9 "/path/to/file.pdf"
```

---

## 4. Information — 信息获取

```bash
xb run get text @ref                # 获取元素文本内容
xb run get html @ref                # 获取元素 innerHTML
xb run get value @ref               # 获取表单元素当前值
xb run get attr @ref <attr>         # 获取元素属性值
xb run get title                    # 获取页面标题
xb run get url                      # 获取页面 URL
xb run get cdp-url                  # 获取 CDP 连接 URL
xb run get count <selector>         # 匹配选择器的元素数量
xb run get box @ref                 # 获取元素边界框 (x, y, w, h)
xb run get styles @ref              # 获取元素计算样式
```

```bash
xb run get attr @e10 "href"
xb run get count "table tbody tr"
xb run get url
```

---

## 5. State Check — 状态检查

```bash
xb run is visible @ref              # 元素是否可见 → true/false
xb run is enabled @ref              # 元素是否启用（非 disabled）
xb run is checked @ref              # 复选框/单选按钮是否勾选
```

---

## 6. Screenshots & PDF — 截图与导出

```bash
xb run screenshot [path]            # 截图，省略路径则输出 base64
xb run screenshot --full            # 截取完整页面（含滚动区域）
xb run screenshot --annotate        # 截图标注 ref 编号
xb run pdf <path>                   # 导出 PDF
```

```bash
xb run screenshot --full --annotate
xb run pdf "/tmp/report.pdf"
```

---

## 7. Wait — 等待条件

```bash
xb run wait @ref                    # 等待元素出现并可见
xb run wait <ms>                    # 等待指定毫秒数
xb run wait --text "..."            # 等待页面出现指定文本
xb run wait --url "..."             # 等待 URL 匹配模式（支持 glob）
xb run wait --load networkidle      # 等待网络空闲
xb run wait --fn "expression"       # 等待 JS 表达式返回真值
```

```bash
xb run wait 2000
xb run wait --text "加载完成"
xb run wait --url "**/dashboard"
xb run wait --load networkidle
```

---

## 8. Mouse Control — 鼠标控制

低层级操作，用于无法通过 `@ref` 完成的精细控制。

```bash
xb run mouse move <x> <y>           # 移动鼠标到坐标
xb run mouse down <btn>             # 按下按键：left/right/middle
xb run mouse up <btn>               # 释放按键
xb run mouse wheel <delta>          # 滚轮，正值向下，负值向上
```

```bash
xb run mouse move 100 200
xb run mouse wheel -300
```

---

## 9. Keyboard — 键盘控制

```bash
xb run keyboard type "text"         # 键盘输入文本
xb run keyboard inserttext "text"   # 插入文本（不触发按键事件）
```

---

## 10. Semantic Locators — 语义定位

通过语义属性定位元素并执行操作，无需 `@ref`。

```bash
xb run find role <role> <action> [--name "..."]    # 按 ARIA role 定位
xb run find text "..." <action>                     # 按可见文本定位
xb run find label "..." <action>                    # 按 label 文本定位
xb run find placeholder "..." <action>              # 按 placeholder 定位
xb run find alt "..." <action>                      # 按 alt 文本定位
xb run find title "..." <action>                    # 按 title 属性定位
xb run find testid "..." <action>                   # 按 data-testid 定位
xb run find first <selector> <action>               # CSS 选择器第一个匹配
xb run find last <selector> <action>                # CSS 选择器最后一个匹配
xb run find nth <n> <selector> <action>             # CSS 选择器第 n 个（从 0 起）
```

```bash
xb run find role button click --name "Submit"
xb run find role textbox fill "hello" --name "Email"
xb run find text "Sign in" click
xb run find label "Password" fill "secret123"
xb run find nth 2 "ul > li" click
```

---

## 11. Browser Settings — 浏览器设置

```bash
xb run set viewport <w> <h>         # 设置视口尺寸
xb run set device "name"            # 模拟预定义设备（视口/UA/DPR）
xb run set geo <lat> <lng>          # 设置地理位置
xb run set offline on|off           # 离线模式开关
xb run set headers '{...}'          # 设置额外 HTTP 请求头（JSON）
xb run set credentials <user> <pass>  # 设置 HTTP Basic Auth 凭据
xb run set media dark|light         # 设置 prefers-color-scheme
```

```bash
xb run set viewport 375 812
xb run set device "iPhone 14"
xb run set geo 39.9042 116.4074
xb run set headers '{"Accept-Language": "zh-CN"}'
```

---

## 12. Cookies & Storage — Cookie 与存储

```bash
xb run cookies                      # 列出所有 Cookie
xb run cookies set <name> <value>   # 设置 Cookie
xb run cookies clear                # 清除所有 Cookie
xb run storage local                # 列出所有 localStorage
xb run storage local <key>          # 获取指定 key
xb run storage local set <k> <v>    # 设置键值对
xb run storage local clear          # 清除所有 localStorage
xb run storage session              # 列出所有 sessionStorage
xb run storage session <key>        # 获取指定 key
xb run storage session set <k> <v>  # 设置键值对
xb run storage session clear        # 清除所有 sessionStorage
```

```bash
xb run cookies set "session_id" "abc123"
xb run storage local set "theme" "dark"
```

---

## 13. Network — 网络拦截与监控

```bash
xb run network route <pattern>                # 拦截匹配请求（放行并记录）
xb run network route <pattern> --abort        # 中断匹配请求
xb run network route <pattern> --body '{...}' # 替换响应体
xb run network unroute [pattern]              # 移除拦截规则（省略则移除全部）
xb run network requests                       # 列出已捕获请求
xb run network requests --filter <pattern>    # 按 URL 模式过滤
xb run network request <url>                  # 获取指定请求详情
xb run network har start                      # 开始 HAR 录制
xb run network har stop <file>                # 停止 HAR 录制并保存
```

```bash
xb run network route "**/api/ads" --abort
xb run network route "**/api/config" --body '{"feature_flag": true}'
xb run network requests --filter "api"
xb run network har stop "/tmp/trace.har"
```

---

## 14. Tabs & Windows — 标签页与窗口

```bash
xb run tab                          # 列出所有标签页
xb run tab new [url]                # 新建标签页，可选加载 URL
xb run tab <n>                      # 切换到第 n 个标签页（从 0 起）
xb run tab close                    # 关闭当前标签页
xb run window new                   # 打开新窗口
```

```bash
xb run tab new "https://example.com"
xb run tab 0
```

---

## 15. Frames — 框架切换

```bash
xb run frame <selector>             # 切换到指定 iframe
xb run frame main                   # 切换回主框架
```

```bash
xb run frame "#content-frame"
xb run frame "iframe[name='editor']"
```

---

## 16. Dialogs — 对话框处理

```bash
xb run dialog accept [text]         # 确认对话框（prompt 可传入文本）
xb run dialog dismiss               # 取消对话框
xb run dialog status                # 获取对话框状态
```

```bash
xb run dialog accept "confirmed input"
```

---

## 17. JavaScript — 脚本执行

```bash
xb run eval "expression"            # 执行 JS 表达式并返回结果
```

```bash
xb run eval "document.title"
xb run eval "Array.from(document.querySelectorAll('h2')).map(e => e.textContent)"
```

---

## 18. State Management — 状态管理

```bash
xb run state save <file>            # 保存浏览器状态（Cookie/Storage）到文件
xb run state load <file>            # 从文件恢复状态
xb run state list                   # 列出已保存的状态
xb run state show <name>            # 查看状态详情
xb run state rename <old> <new>     # 重命名状态
xb run state clear                  # 清除所有状态
xb run state clean                  # 清除过期状态
```

```bash
xb run state save "/tmp/logged-in.json"
xb run state load "/tmp/logged-in.json"
xb run state list
```

---

## 19. Sessions — 会话管理

xb 自动管理每个浏览器的会话（`xbrowser-cft`、`xbrowser-chrome` 等），无需手动指定。

```bash
xb run session list                 # 列出活跃会话
```

---

## 20. Batch Execution — 批量执行

```bash
xb run batch "cmd1" "cmd2" ...           # 顺序执行，失败继续
xb run batch --bail "cmd1" "cmd2" ...    # 顺序执行，首个失败即停止
```

```bash
xb run batch "open https://example.com" "snapshot -i" "click @e3"
xb run batch --bail "fill @e7 'query'" "click @e8" "wait --text 'Results'"
```

---

## 21. Clipboard — 剪贴板

```bash
xb run clipboard read               # 读取剪贴板内容
xb run clipboard write "text"       # 写入剪贴板
xb run clipboard copy @ref          # 复制元素内容到剪贴板
xb run clipboard paste @ref         # 粘贴剪贴板内容到元素
```

---

## 22. Recording — 录制

```bash
xb run record start <path>          # 开始录制视频
xb run record stop                  # 停止录制
xb run record restart <path>        # 停止并以新路径重新录制
```

```bash
xb run record start "/tmp/session.webm"
```

---

## 23. Debugging — 调试工具

```bash
xb run console                      # 显示控制台日志
xb run errors                       # 显示 JS 错误
xb run highlight @ref               # 高亮元素（需 --headed）
xb run inspect @ref                 # 检查元素详细信息
xb run trace start                  # 开始 Playwright trace 录制
xb run trace stop <file>            # 停止并保存 trace
xb run profiler start               # 开始性能分析
xb run profiler stop                # 停止性能分析
```

```bash
xb run --headed highlight @e5
xb run trace stop "/tmp/trace.zip"
```

---

## 24. Diff — 变更对比

```bash
xb run diff snapshot                # 对比两次快照的差异
xb run diff screenshot              # 对比两次截图的差异
xb run diff url                     # 对比 URL 变化
```

---

## 25. Stream — 流式输出

```bash
xb run stream enable                # 开启流式输出模式
xb run stream status                # 查看流式输出状态
xb run stream disable               # 关闭流式输出模式
```

---

## 快速参考索引

| 类别 | 常用命令 |
|------|---------|
| 导航 | `open`, `back`, `forward`, `reload`, `close` |
| 快照 | `snapshot`, `snapshot -i -c` |
| 交互 | `click`, `fill`, `type`, `press`, `select`, `scroll` |
| 信息 | `get text`, `get url`, `get title`, `get attr` |
| 状态检查 | `is visible`, `is enabled`, `is checked` |
| 截图 | `screenshot`, `screenshot --full`, `pdf` |
| 等待 | `wait @ref`, `wait --text`, `wait --load networkidle` |
| 鼠标 | `mouse move`, `mouse down`, `mouse up`, `mouse wheel` |
| 键盘 | `keyboard type`, `keyboard inserttext` |
| 语义定位 | `find role`, `find text`, `find label` |
| 设置 | `set viewport`, `set device`, `set media` |
| 存储 | `cookies`, `storage local`, `storage session` |
| 网络 | `network route`, `network requests`, `network har` |
| 标签页 | `tab`, `tab new`, `tab close` |
| 框架 | `frame`, `frame main` |
| 对话框 | `dialog accept`, `dialog dismiss` |
| 脚本 | `eval` |
| 状态管理 | `state save`, `state load` |
| 会话 | `session list` |
| 批量 | `batch`, `batch --bail` |
| 剪贴板 | `clipboard read`, `clipboard write`, `clipboard copy`, `clipboard paste` |
| 录制 | `record start`, `record stop` |
| 调试 | `console`, `errors`, `trace start`, `highlight`, `inspect` |
| 变更对比 | `diff snapshot`, `diff screenshot`, `diff url` |
| 流式输出 | `stream enable`, `stream disable` |
