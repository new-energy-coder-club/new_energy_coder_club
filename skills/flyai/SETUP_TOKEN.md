# Token Setup

> `get-token.sh` / `get-token.ps1` are located in the same directory as this file.
> Replace `<SCRIPT_PATH>` with the absolute path of this file's directory before running.

## Important: Obtain and inject API Key at the start of every session

Each command execution runs in an independent shell process, so the API Key must be obtained and injected into `flyai-cli` config **at session start**. Once injected, all subsequent `flyai` commands in the same session can use it without re-fetching.

### macOS / Linux

```bash
# ✅ At session start: obtain API Key and inject into flyai-cli
api_key=$(bash '<SCRIPT_PATH>/get-token.sh') && flyai config set FLYAI_API_KEY "$api_key"
```

```bash
# Then run commands as usual
flyai keyword-search --query "what to do in Sanya"
```

### Windows (PowerShell)

```powershell
# ✅ At session start: obtain API Key and inject into flyai-cli
$apiKey = & "<SCRIPT_PATH>\get-token.ps1"
flyai config set FLYAI_API_KEY $apiKey
```

```powershell
# Then run commands as usual
flyai keyword-search --query "what to do in Sanya"
```

## Error Handling

If the script outputs `ERROR` or returns an empty value:
- The user has not yet authorized FlyAI in the **in-app integration panel**
- Prompt the user: go to the integration panel → click FlyAI → enter the authorization code → complete authorization, then retry
- Guide link: **https://qclaw.qq.com/docs/208142370404184064.html**
