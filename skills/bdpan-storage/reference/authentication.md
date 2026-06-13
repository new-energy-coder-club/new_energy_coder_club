# 认证指南

本指南详细介绍 bdpan CLI 的登录认证流程。

---

## 登录前免责声明（强制）

**无论通过哪种方式登录，在执行登录命令之前，必须先向用户展示安全须知与免责声明，并获得用户确认。**

免责声明内容参见 [reference/notes.md](./notes.md)。

- **login.sh 脚本（唯一入口）**：脚本内置了免责声明展示和确认流程，**Agent 必须且只能通过此脚本执行登录**
- **⛔ 严禁 Agent 直接调用** `bdpan login --get-auth-url`、`bdpan login --set-code` 或任何 bdpan login 子命令
- **自动化场景**：login.sh 支持 `--yes` 参数跳过确认，但仅限用户已在对话中明确表达登录意图的场景

---

## 登录方式

**强制要求：必须使用登录脚本**

> **⛔ Agent 必须且只能通过 login.sh 脚本执行登录，严禁直接调用 bdpan login 子命令。**
>
> **⛔ 即使在 GUI 环境（macOS、桌面 Linux），也禁止使用 `bdpan login` 直接弹出 WebView。**

```bash
bash scripts/login.sh
```

脚本会自动处理完整的登录流程（免责声明 → 用户确认 → 获取授权链接 → 校验授权码 → 完成登录）。

---

## 验证登录状态

### 查看当前登录状态

```bash
bdpan whoami
```

**输出示例：**
```
认证状态: 已登录
Token 有效期至: 2026-03-10 10:30:00
```

**未登录时输出：**
```
认证状态: 未登录
请执行 bdpan login 进行登录
```

---

## 注销登录

```bash
bdpan logout
```

清除本地存储的认证信息（`~/.config/bdpan/config.json`）。

---

## 常见问题

### 登录后提示 Token 已过期

**症状：**
```
错误: Token 过期
Error: Token expired
```

**解决方案：**
```bash
bdpan logout
bash scripts/login.sh
```

### 授权链接无效

**症状：** 浏览器打开链接后提示链接无效

**解决方案：**
1. 重新执行 `bash scripts/login.sh` 获取新的授权链接
2. 确保在链接有效期内完成授权（通常 10 分钟）

### 授权码输入后报错

**症状：** 输入授权码后提示错误

**解决方案：**
1. 确保授权码复制完整，没有多余空格
2. 检查浏览器中显示的授权码是否与输入的一致
3. 如多次失败，重新执行 `bash scripts/login.sh` 获取新授权码

> **⛔ 注意：** 以上所有登录操作必须通过 `bash scripts/login.sh` 脚本执行，禁止直接使用 `bdpan login`。

---

## 配置文件位置

```
~/.config/bdpan/config.json
```

**环境变量：**

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `BDPAN_CONFIG_DIR` | 配置文件目录 | `~/.config/bdpan` |

---

## 安全说明

- **OAuth 2.0**：使用授权码模式，不存储用户密码
- **Token 存储**：Token 加密存储在本地配置文件
- **自动续期**：Token 快过期时工具会自动刷新

---

## 自动登录失败场景

以下场景会自动切换到 OOB 模式：

| 场景 | 说明 |
|------|------|
| SSH 远程登录 | 无图形界面 |
| WSL 环境 | WebView 支持受限 |
| 桌面环境锁定 | WebView 无法弹出 |
| 浏览器未安装 | 无法打开 WebView |

切换到 OOB 模式时，工具会自动提示授权链接，无需用户干预。
