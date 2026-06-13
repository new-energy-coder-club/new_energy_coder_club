# Token 初始化

> `get-token.sh` / `get-token.ps1` 与本文件位于同一目录下。
> 执行前将 `<SCRIPT_PATH>` 替换为本文件所在目录的绝对路径。

## 重要：每次会话开始时自动获取并注入 API Key

由于每次命令执行都是独立的 shell 进程，API Key 需要在**会话开始时**通过脚本获取并注入 CLI 配置。
注入后同一会话内所有 `youdaonote` 命令均可直接使用，无需重复获取。

### macOS / Linux — 使用方式

```bash
# ✅ 会话开始时：获取 API Key 并注入 CLI 配置
api_key=$(bash '<SCRIPT_PATH>/get-token.sh') && youdaonote config set apiKey "$api_key"
```

```bash
# 然后正常执行命令
youdaonote list
youdaonote search "关键词"
```

### Windows (PowerShell) — 使用方式

```powershell
# ✅ 会话开始时：获取 API Key 并注入 CLI 配置
$apiKey = & "<SCRIPT_PATH>\get-token.ps1"
youdaonote config set apiKey $apiKey
```

```powershell
# 然后正常执行命令
youdaonote list
youdaonote search "关键词"
```

## 失败处理

如果脚本输出 `ERROR` 或返回空值：
- 用户尚未在**应用内集成面板**中完成有道云笔记授权
- 请提示用户：在集成面板中点击有道云笔记 → 输入 API Key → 完成授权，然后重试
- API Key 获取地址：**https://mopen.163.com**（须使用手机号登录，且云笔记账号已绑定手机号）
