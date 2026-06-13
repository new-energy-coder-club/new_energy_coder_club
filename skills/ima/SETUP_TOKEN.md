# Token 初始化

> `get-token.sh` / `get-token.ps1` 与本文件位于同一目录下。
> 执行前将 `<SCRIPT_PATH>` 替换为本文件所在目录的绝对路径。

## 重要：每条命令都要内联获取凭证

由于每次命令执行都是独立的 shell 进程，`export` 设置的环境变量**不会**传递到下一条命令。
因此，**不要**分两步（先 export 再 curl），而是在每条 API 调用命令中内联获取凭证：

### macOS / Linux — 使用方式

```bash
# ✅ 正确：内联获取凭证，直接用于 curl
CREDS=$(bash '<SCRIPT_PATH>/get-token.sh') && \
curl -s -X POST "https://ima.qq.com/openapi/note/v1/search_note_book" \
  -H "ima-openapi-clientid: $(echo "$CREDS" | jq -r .client_id)" \
  -H "ima-openapi-apikey: $(echo "$CREDS" | jq -r .api_key)" \
  -H "Content-Type: application/json" \
  -d '{"search_type": 0, "query_info": {"title": "测试"}, "start": 0, "end": 20}'
```

```bash
# ❌ 错误：export 在下一条命令中无效
export IMA_CREDS=$(bash '<SCRIPT_PATH>/get-token.sh')
# 下一条 execute_command 中 $IMA_CREDS 为空！
```

### Windows (PowerShell) — 使用方式

```powershell
# ✅ 正确：内联获取凭证
$creds = & "<SCRIPT_PATH>\get-token.ps1" | ConvertFrom-Json
$headers = @{
  "ima-openapi-clientid" = $creds.client_id
  "ima-openapi-apikey" = $creds.api_key
}
irm "https://ima.qq.com/openapi/note/v1/search_note_book" -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"search_type": 0, "query_info": {"title": "测试"}, "start": 0, "end": 20}'
```

## 失败处理

如果脚本输出 `ERROR` 或返回空值：

**平台托管模式**（AUTH_GATEWAY_PORT 已设置）：
- 用户尚未在**应用内集成面板**中完成 IMA 授权
- 请提示用户：在集成面板中完成 IMA 授权，然后重试

**本地模式**（无 AUTH_GATEWAY_PORT）：
- 缺少 IMA 凭证配置
- 请提示用户按 Setup 步骤配置 Client ID 和 API Key（环境变量或配置文件）
