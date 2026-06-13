# Debug Server Minimal Template (Fallback Reference)

## Warning
**Before attempting to implement this template, ensure you have confirmed that the built-in Python/Node scripts cannot run in the current environment.**

## Goal
When built-in scripts are both unavailable, quickly implement a minimal HTTP log collector based on the current environment (e.g., Go, Rust, Ruby, etc.).

## Architecture
The Debug Server is an HTTP server that:
1. Listens on a configurable port (default: 7777)
2. Accepts POST requests to `/event` endpoint
3. Parses JSON event data
4. Appends events to `<outdir>/trae-debug-log-<sessionId>.ndjson` file
5. Writes environment file `<outdir>/<sessionId>.env` for zero-config instrumentation

## Required Arguments
- `--session`: **Required.** A semantic session identifier (e.g., `login-500-error`, `cart-empty-bug`)
- `--port`: Starting port (default: 7777)
- `--outdir`: Output directory (default: `.dbg`)
- `--clean`: Clear existing log file for this session on startup
- `--idle`: Auto-exit after N seconds of inactivity
- `--remote`: Listen on 0.0.0.0 and detect local IP

## Required Endpoints

### POST /event
- Accept JSON body with event data
- Append to session-specific NDJSON file
- Return 200 OK on success

### OPTIONS /event (CORS preflight)
- Return 204 with CORS headers for browser compatibility

## Required CORS Headers
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## Event Schema (Required Fields)
- `sessionId`: Grouping identifier (used for filename)
- `runId`: Phase identifier (e.g., `"pre-fix"`, `"post-fix"`)
- `hypothesisId`: Scientific hypothesis link (A/B/C/D/E)
- `msg`: Short description with log prefix
- `ts`: Timestamp (auto-fill with server time if omitted)

## Environment File Output
The server must write an env file on startup:

**File**: `<outdir>/<sessionId>.env`

**Content**:
```
DEBUG_SERVER_URL=http://<host>:<actual_port>/event
DEBUG_SESSION_ID=<sessionId>
```

## Pseudocode

```python
def write_env_file(outdir, session_id, api_url):
    filepath = f"{outdir}/{session_id}.env"
    write_file(filepath, f"DEBUG_SERVER_URL={api_url}\nDEBUG_SESSION_ID={session_id}\n")
    return filepath

def handle_post(request):
    event = json.parse(request.body)
    session_id = event.get("sessionId", "default")
    
    if "ts" not in event:
        event["ts"] = current_time_ms()
    
    filepath = f"{outdir}/trae-debug-log-{session_id}.ndjson"
    append_line(filepath, json.stringify(event))
    
    return Response(200, "ok")

def handle_options(request):
    return Response(204, headers=CORS_HEADERS)

# On startup
api_url = f"http://{host}:{actual_port}/event"
env_file = write_env_file(outdir, session_id, api_url)

server.route("POST", "/event", handle_post)
server.route("OPTIONS", "/event", handle_options)
server.listen(port, host)
```

## Required Features
1. **Port auto-probing**: If default port is occupied, try incrementing ports (max 10 retries)
2. **CORS support**: Allow browser-side reporting
3. **Idle timeout** (optional): Auto-exit after N seconds of inactivity
4. **Clean mode** (optional): Truncate existing session log file on startup
5. **Environment file output**: Write `.env` file with server URL and session ID

## Startup Output
Must output the following structured marker for Agent to detect configuration:
```
@@DEBUG_SERVER_INFO
{
  "api_url": "http://<host>:<port>/event",
  "session_id": "<sessionId>",
  "log_dir": "<absolute_outdir>",
  "log_file": "<absolute_outdir>/trae-debug-log-<sessionId>.ndjson",
  "env_file": "<absolute_outdir>/<sessionId>.env"
}
@@END_DEBUG_SERVER_INFO
```

## Notes
- Use only standard library (no third-party dependencies)
- Ensure atomic file appends for multi-process safety
- Handle JSON parse errors gracefully (return 400)
- Session ID is provided at startup via `--session`, not derived from events
