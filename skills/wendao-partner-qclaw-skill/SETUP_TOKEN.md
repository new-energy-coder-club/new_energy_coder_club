# Token Setup

> `get-token.sh` / `get-token.ps1` are located in the same directory as this file.
> Replace `<SCRIPT_PATH>` with the absolute path of this file's directory before running.

## Important: Obtain and inject API Key at the start of every session

Each command execution runs in an independent shell process, so the API Key must be obtained and injected into the environment **at session start**. Once injected, all subsequent commands in the same session can use it without re-fetching.

### macOS / Linux

```bash
# ✅ At session start: obtain API Key from credential hosting
export WENDAO_API_KEY=$(bash '<SCRIPT_PATH>/get-token.sh')
```

```bash
# Then run commands as usual
node scripts/wendao_query.js "我想去三亚玩三天，帮我规划行程"
```

### Windows (PowerShell)

```powershell
# ✅ At session start: obtain API Key from credential hosting
$env:WENDAO_API_KEY = & "<SCRIPT_PATH>\get-token.ps1"
```

```powershell
# Then run commands as usual
node scripts/wendao_query.js "我想去三亚玩三天，帮我规划行程"
```

## Error Handling

If the script outputs `ERROR` or returns an empty value:
- The user has not yet authorized 携程问道 in the **in-app integration panel**
- Prompt the user: go to the integration panel → click 携程问道 → enter the authorization code → complete authorization, then retry
- Guide link: **https://qclaw.qq.com/docs/208231741261246464.html**
