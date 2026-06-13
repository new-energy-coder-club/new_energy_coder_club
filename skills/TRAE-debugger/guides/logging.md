## Logging System (Native API Reporting)

### A. Reporting Strategy (Mandatory Server Aggregation)

To ensure that logs from multiple sources can be analyzed uniformly, **all debugging logs must be reported via network requests to the Debug Server**.

#### 1. Core Requirements
*   **One-liner**: Must use native capabilities, invoked in a "one-line code" format.
*   **Collapsible Regions**: **Must** use `#region` / `#endregion` to wrap instrumentation points, preventing pollution of the editor view.
*   **Log Prefix**: **Must** use the project log prefix. If the user has specified one (e.g., `[ISSUE-1]`), that prefix must be used; if not specified, `[DEBUG]` is used by default. The prefix should be placed at the very beginning of the `msg` field.
*   **3–8 Key Points**: Cover function entry/exit, before/after critical operations, branch paths, edge cases, and state changes.
*   **Env File Configuration**: Prefer reading `DEBUG_SERVER_URL` and `DEBUG_SESSION_ID` from the env file (`.dbg/<sessionId>.env`) to avoid hardcoding URLs.

#### Language-Specific Region Syntax

| Language | Region Start | Region End | Example |
|----------|--------------|------------|---------|
| JavaScript/TypeScript | `// #region debug-point <id>` | `// #endregion` | `// #region debug-point A:init` |
| Python | `# #region debug-point <id>` | `# #endregion` | `# #region debug-point B:auth` |
| Go | `// #region debug-point <id>` | `// #endregion` | `// #region debug-point C:db` |
| Rust | `// #region debug-point <id>` | `// #endregion` | `// #region debug-point D:parse` |
| Ruby | `# #region debug-point <id>` | `# #endregion` | `# #region debug-point E:cache` |
| Shell/Bash | `# #region debug-point <id>` | `# #endregion` | `# #region debug-point A:env` |
| HTML | `<!-- #region debug-point <id> -->` | `<!-- #endregion -->` | `<!-- #region debug-point A:dom -->` |
| CSS | `/* #region debug-point <id> */` | `/* #endregion */` | `/* #region debug-point A:style */` |

**Note**: The `<id>` format is `<hypothesisId>[:description]`, e.g., `A:check-state` or just `A`.

#### 2. Code Templates (Env File Based - Recommended)

**Browser / Node.js (Read env file, with fallback):**
```js
// #region debug-point A:check-state
(()=>{const fs=require('fs'),p='.dbg/login-500-error.env';let u='http://127.0.0.1:7777/event',s='login-500-error';try{const e=fs.readFileSync(p,'utf8');u=e.match(/DEBUG_SERVER_URL=(.+)/)?.[1]||u;s=e.match(/DEBUG_SESSION_ID=(.+)/)?.[1]||s}catch{}fetch(u,{method:'POST',body:JSON.stringify({sessionId:s,runId:'pre',hypothesisId:'A',location:'file.js:42',msg:'[DEBUG] ...',data:{},ts:Date.now()})}).catch(()=>{})})();
// #endregion
```

**Browser (No file access - use hardcoded URL from env file):**
```js
// #region debug-point A:check-state
fetch("http://127.0.0.1:<port>/event",{method:"POST",body:JSON.stringify({sessionId:"login-500-error",runId:"pre",hypothesisId:"A",location:"file.js:42",msg:"[DEBUG] ...",data:{},ts:Date.now()})}).catch(()=>{});
// #endregion
```

**Python (Read env file, with fallback):**
```python
# #region debug-point B:api-call
import json, urllib.request, os; _p='.dbg/login-500-error.env'; _u,_s='http://127.0.0.1:7777/event','login-500-error'; exec("try:\n with open(_p) as f: c=f.read(); _u=next((l.split('=',1)[1] for l in c.split('\\n') if l.startswith('DEBUG_SERVER_URL=')),_u); _s=next((l.split('=',1)[1] for l in c.split('\\n') if l.startswith('DEBUG_SESSION_ID=')),_s)\nexcept: pass"); urllib.request.urlopen(urllib.request.Request(_u, data=json.dumps({"sessionId":_s,"runId":"pre","hypothesisId":"B","location":"main.py:10","msg":"[DEBUG] ..."}).encode(), headers={"Content-Type":"application/json"})).read()
# #endregion
```

**Shell/Bash (Read env file):**
```bash
# #region debug-point C:env-vars
source .dbg/login-500-error.env 2>/dev/null || { DEBUG_SERVER_URL="http://127.0.0.1:7777/event"; DEBUG_SESSION_ID="login-500-error"; }; curl -sX POST "$DEBUG_SERVER_URL" -d "{\"sessionId\":\"$DEBUG_SESSION_ID\",\"runId\":\"pre\",\"hypothesisId\":\"C\",\"location\":\"shell\",\"msg\":\"[DEBUG] ...\"}"
# #endregion
```

#### 3. Legacy Templates (Hardcoded URL - Use when env file not accessible)

*   **Browser / Node.js (Fetch API)**:
    ```js
    // #region debug-point A:check-state
    fetch("http://127.0.0.1:<port>/event",{method:"POST",body:JSON.stringify({sessionId:"login-500-error",runId:"pre",hypothesisId:"A",location:"file.js:42",msg:"[DEBUG] ...",data:{},ts:Date.now()})}).catch(()=>{});
    // #endregion
    ```
*   **Python (Standard Library)**:
    ```python
    # #region debug-point B:api-call
    import json, urllib.request; urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:<port>/event", data=json.dumps({"sessionId":"login-500-error","runId":"pre","hypothesisId":"B","location":"main.py:10","msg":"[DEBUG] ..."}).encode(), headers={"Content-Type":"application/json"})).read()
    # #endregion
    ```
*   **Other (cURL)**:
    ```bash
    # #region debug-point C:env-vars
    curl -X POST http://127.0.0.1:<port>/event -d '{"sessionId":"login-500-error","runId":"pre","hypothesisId":"C","location":"shell","msg":"[DEBUG] ..."}'
    # #endregion
    ```

> **💡 Note**: Replace `<port>` with the actual port from Debug Server output. The `sessionId` should match your semantic session identifier.

### B. NDJSON Storage Format
Upon receiving an HTTP POST, the Debug Server appends the data to `trae-debug-log-<sessionId>.ndjson` in the output directory. The Agent should read logs from this file for analysis.

### C. Event Structure (MUST include)

* `sessionId`: Debug session identifier.
* `runId`: Run identifier (e.g., `"pre-fix"`, `"post-fix"`).
* `hypothesisId`: Corresponding hypothesis (A/B/C/D/E).
* `ts`: Timestamp (ms), auto-filled by server if omitted.
* `location`: File:Line / Module identifier (optional but recommended).
* `msg`: Short description with log prefix (e.g., `"[DEBUG] State updated"`).
* `data`: Structured fields (minimal and critical).
* `traceId` (Optional): Single request/operation trace ID.
