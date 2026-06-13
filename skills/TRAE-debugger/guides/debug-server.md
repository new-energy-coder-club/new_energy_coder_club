## Debug Server (Runtime Evidence Collection Tool)

This Skill provides a Python-based Debug Server script.

> **⚠️ MUST use the exact script path below. Do NOT invent commands like `npx trae-debugger` or `trae-debug-server` — they don't exist.**

### Startup

```bash
# Local Debugging
python3 c:\Users\29711\.trae\builtin_skills\TRAE-debugger/tools/debug-server/python/debug-server.py --session <sessionId> --outdir .dbg --clean --idle 1200

# Remote/Mobile Debugging (Auto-detect IP)
python3 c:\Users\29711\.trae\builtin_skills\TRAE-debugger/tools/debug-server/python/debug-server.py --remote --session <sessionId> --outdir .dbg --clean --idle 1200
```

**❌ Wrong (do NOT use)**:
```bash
npx trae-debugger start --session xxx        # Does not exist
trae-debug-server --session xxx              # Does not exist
node debug-server.js --session xxx           # Does not exist
```

**Parameters**:
- `--session`: **Required.** Semantic session ID (e.g., `login-500-error`)
- `--clean`: Clear existing logs for this session on startup
- `--idle`: Auto-exit after N seconds of inactivity (default: 0 = never)
- `--port`: Starting port (default: 7777, auto-probes if occupied)
- `--remote`: Listen on `0.0.0.0` and show local IP for mobile/remote access

### Core Features

- **Zero Dependencies**: Uses Python standard library only
- **CORS Support**: Allows browser-side reporting
- **Auto Port Probing**: Tries next port if occupied (up to 10 retries)
- **Environment File**: Writes `<sessionId>.env` for zero-config instrumentation

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/event` | Submit log event |
| `GET` | `/health` | Health check (status, uptime, log count) |
| `GET` | `/logs` | Get all logs (`?last=N`, `?hypothesisId=A`, `?runId=pre`) |
| `DELETE` | `/logs` | Clear logs for current session |

### Environment File

On startup, the server writes `.dbg/<sessionId>.env`:

```
DEBUG_SERVER_URL=http://127.0.0.1:<port>/event
DEBUG_SESSION_ID=<sessionId>
```

Instrumentation code can read this file to auto-configure.

### Lifecycle

- **Start**: At workflow Step 3, before instrumentation
- **During**: Keep running throughout debugging session
- **Stop**: After user confirms fix (Step 11)
- **Security**: `--remote` exposes to local network; use in trusted environments only

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| `Port occupied` loops | Kill process: `lsof -i :7777` then `kill <PID>` |
| `python3: command not found` | Install Python 3.6+ |
| Mobile can't connect | Use `--remote` mode |
| No logs received | Verify URL matches server output |

### Fallback

If Python is unavailable, refer to `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/tools/debug-server/TEMPLATE.md` to implement a minimal collector in your environment's language.
