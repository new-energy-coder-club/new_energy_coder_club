# 故障排查

常见问题及解决方案。

---

## xb setup 失败

### 网络问题

`xb setup` 自动从 npm registry 下载底层引擎，按以下优先级选择镜像源：

1. 腾讯镜像 (`mirrors.tencent.com/npm`)
2. npmmirror (`registry.npmmirror.com`)
3. npm 官方源 (`registry.npmjs.org`)

如果安装失败，检查网络连通性：

```bash
# 测试腾讯镜像
curl -sI https://mirrors.tencent.com/npm/

# 测试 npmmirror
curl -sI https://registry.npmmirror.com/
```

### 代理设置

如果处于需要代理的网络环境，确保环境变量已设置：

```bash
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

### 浏览器引擎下载失败

`xb setup` 默认从 Google CDN 下载 Chrome for Testing，国内网络可能超时。

**替代方案**：

1. **手动下载**：访问 [Chrome for Testing 版本列表](https://googlechromelabs.github.io/chrome-for-testing/) 获取下载链接，通过代理或 VPN 下载对应平台的压缩包
2. **使用系统浏览器**：切换到已安装的 Chrome/Edge/QQ 浏览器：
   ```bash
   xb config set browser chrome
   # 或
   xb config set browser edge
   ```

### 权限问题（Linux/macOS）

| 错误 | 解决方案 |
|------|---------|
| `permission denied` | 检查 xb 目录的写权限 |
| 浏览器无法启动 | Linux 可能缺少系统库依赖 |

---

## 浏览器操作超时

### 症状

`xb run open <url>` 返回 `ok=false`，error 包含 "超时"。

### 排查步骤

1. **增加超时时间**：
   ```bash
   xb run --timeout 29000 open https://slow-site.com
   ```

2. **检查当前 URL**（确认是否部分加载）：
   ```bash
   xb run get url
   ```

3. **等待网络空闲**：
   ```bash
   xb run wait --load networkidle
   ```

4. **使用有头模式调试**（查看浏览器实际状态）：
   ```bash
   xb run --headed open https://example.com
   ```

---

## 元素不存在 / @ref 失效

### 症状

`xb run click @e5` 返回 `ok=false`，error 包含 "元素引用已失效" 或 "not found"。

### 原因

`@ref` 是临时的，页面 DOM 变化（导航、AJAX、动画）后会失效。

### 解决方案

重新获取快照，使用新的 @ref：

```bash
xb run snapshot -i
# 使用新返回的 @ref 编号
xb run click @e3
```

---

## 浏览器进程残留

### 症状

`xb run --browser chrome` 返回 `ok=false`，error 包含“正在运行但未启用 CDP”。

### 原因

之前的浏览器进程未正常退出（headless 进程残留）。

### 解决方案

```bash
xb stop chrome    # 关闭 Chrome
xb stop all       # 关闭所有本地浏览器
```

关闭后重新执行操作即可。

---

## 浏览器未安装

### 症状

`xb init` 返回 `ok=false`，error 包含 "未安装"。

### 解决方案

1. **安装浏览器引擎**（默认 Chrome for Testing）：
   ```bash
   xb setup
   ```

2. **或切换到已安装的系统浏览器**：
   ```bash
   xb config set browser chrome    # 使用系统 Chrome
   xb config set browser edge      # 使用系统 Edge
   xb config set browser qqbrowser # 使用 QQ 浏览器
   ```

3. **重新初始化**：
   ```bash
   xb init
   ```

---

## 配置问题

### 配置未完成

`xb init` 返回 `ok=false`，error 包含 "配置未完成"。

```bash
# 重置为默认配置
xb config reset

# 重新初始化
xb init
```

### 查看当前配置

```bash
xb config show
```

### 修改配置

```bash
xb config set browser edge
xb config set headed true
```

### 配置引导

```bash
xb guide config
```

---

## 国内网络问题（China Network）

### npm 源不可达

setup 脚本自动使用国内镜像，但如果所有镜像都不可达：

```bash
# 手动测试各镜像源
curl -sI https://mirrors.tencent.com/npm/
curl -sI https://registry.npmmirror.com/
curl -sI https://registry.npmjs.org/
```

### Chrome for Testing 下载问题

Google CDN 在国内可能无法访问。手动下载方案：

1. 访问 [Chrome for Testing 版本列表](https://googlechromelabs.github.io/chrome-for-testing/)
2. 通过可访问的网络下载对应平台的压缩包：
   - macOS (arm64): `chrome-mac-arm64.zip`
   - macOS (x64): `chrome-mac-x64.zip`
   - Windows (x64): `chrome-win64.zip`
   - Linux (x64): `chrome-linux64.zip`
3. 或直接使用系统已安装的浏览器（推荐）：
   ```bash
   xb config set browser chrome
   ```

### 安全提示

> **注意**：使用系统浏览器时，xb 会自动通过 CDP 连接管理，仅监听 localhost。任务完成后运行 `xb cleanup` 清理所有连接。

---

## 常见错误速查

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| "未安装" | 底层引擎未安装 | `xb setup` |
| "需要配置" | 首次使用 | 按 `xb init` 返回的 guide 引导完成 |
| "配置未完成" | 配置不完整 | `xb config reset` |
| "操作超时" | 页面加载慢或网络差 | `xb run --timeout 29000 ...` |
| "元素引用已失效" | DOM 已变化 | `xb run snapshot -i` 重新获取 |
| "浏览器实例已关闭" | 会话断开 | `xb init` 重新初始化 |
| "CLI 未安装" | 引擎缺失 | `xb setup` |
| "页面加载失败" | URL 不可达 | 检查 URL 是否正确 |
| "浏览器引擎启动失败" | daemon 进程异常 | `xb status` 检查 + `xb stop <browser>` |
| "浏览器连接断开" | 连接中断 | `xb cleanup` 后重新执行 |
| "浏览器操作失败" | 未知错误 | 查看 `data.raw_error` 了解详情 |
| "--browser 需要一个值" | 参数缺失 | 补全参数，如 `--browser chrome` |
| "正在运行但未启用 CDP" | 进程残留 | `xb stop <browser>` 后重试 |
| "浏览器可执行文件未找到" | 未安装 | `xb setup` 或 `xb config set browser` |
| "浏览器进程崩溃" | 进程异常 | `xb stop <browser>` 后重试 |
