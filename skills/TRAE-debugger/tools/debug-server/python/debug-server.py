#!/usr/bin/env python3
import http.server
import json
import argparse
import os
import time
from socketserver import TCPServer
from urllib.parse import urlparse, parse_qs

import socket

start_time = time.time()
last_event_ts = time.time()
log_count = 0


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def write_env_file(outdir, session_id, api_url):
    env_path = os.path.join(outdir, f"{session_id}.env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"DEBUG_SERVER_URL={api_url}\n")
        f.write(f"DEBUG_SESSION_ID={session_id}\n")
    return env_path


class Handler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/health":
            global log_count, last_event_ts, start_time
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "session_id": self.server.session_id,
                "uptime": int(time.time() - start_time),
                "log_count": log_count,
                "last_event_ts": int(last_event_ts * 1000)
            }).encode())
            return

        if path == "/logs":
            last_n = int(query.get("last", [0])[0])
            hypothesis_id = query.get("hypothesisId", [None])[0]
            run_id = query.get("runId", [None])[0]

            log_path = os.path.join(
                self.server.outdir,
                f"trae-debug-log-{self.server.session_id}.ndjson"
            )
            logs = []
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                logs.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass

            if hypothesis_id:
                logs = [l for l in logs if l.get("hypothesisId") == hypothesis_id]
            if run_id:
                logs = [l for l in logs if l.get("runId") == run_id]
            if last_n > 0:
                logs = logs[-last_n:]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(logs, ensure_ascii=False).encode())
            return

        self.send_response(404)
        self.end_headers()

    def do_DELETE(self):
        if self.path == "/logs":
            global log_count
            log_path = os.path.join(
                self.server.outdir,
                f"trae-debug-log-{self.server.session_id}.ndjson"
            )
            if os.path.exists(log_path):
                with open(log_path, "w", encoding="utf-8") as f:
                    pass
            log_count = 0
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        global last_event_ts, log_count
        if self.path != "/event":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            event = json.loads(body.decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        session_id = event.get("sessionId", "default")
        if "ts" not in event:
            event["ts"] = int(time.time() * 1000)

        out_path = os.path.join(self.server.outdir, f"trae-debug-log-{session_id}.ndjson")

        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        last_event_ts = time.time()
        log_count += 1
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *_):
        pass


def main():
    global start_time
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7777)
    parser.add_argument("--session", required=True, help="Semantic session ID (e.g., login-500-error, cart-empty-bug)")
    parser.add_argument(
        "--remote", action="store_true", help="Listen on 0.0.0.0 and show local IP"
    )
    parser.add_argument("--outdir", default=".dbg")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--idle", type=int, default=0)
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    
    if args.clean:
        log_file = os.path.join(args.outdir, f"trae-debug-log-{args.session}.ndjson")
        if os.path.exists(log_file):
            with open(log_file, "w") as f_clear:
                pass

    if args.remote:
        args.host = "0.0.0.0"
        local_ip = get_local_ip()
    else:
        local_ip = args.host

    current_port = args.port
    while True:
        try:
            print(f"[Debug Server] Trying http://{args.host}:{current_port}...")
            with TCPServer((args.host, current_port), Handler) as httpd:
                httpd.outdir = args.outdir
                httpd.session_id = args.session
                httpd.timeout = 1
                start_time = time.time()
                display_host = local_ip if args.remote else args.host
                abs_outdir = os.path.abspath(args.outdir)
                base_url = f"http://{display_host}:{current_port}"
                api_url = f"{base_url}/event"
                log_file = f"{abs_outdir}/trae-debug-log-{args.session}.ndjson"
                
                env_file = write_env_file(abs_outdir, args.session, api_url)
                
                print(
                    f"[Debug Server] Listening on http://{display_host}:{current_port}"
                )
                print("@@DEBUG_SERVER_INFO")
                print(json.dumps({
                    "base_url": base_url,
                    "api_url": api_url,
                    "session_id": args.session,
                    "log_dir": abs_outdir,
                    "log_file": log_file,
                    "env_file": env_file,
                    "endpoints": {
                        "POST /event": "Submit log event",
                        "GET /health": "Server health check",
                        "GET /logs": "Get all logs (supports ?last=N&hypothesisId=X&runId=Y)",
                        "DELETE /logs": "Clear all logs for this session"
                    }
                }, indent=2))
                print("@@END_DEBUG_SERVER_INFO")

                while True:
                    httpd.handle_request()
                    if args.idle > 0 and time.time() - last_event_ts > args.idle:
                        print(f"[Debug Server] Idle for {args.idle}s, exiting...")
                        return
        except OSError as e:
            if e.errno in (
                98,
                48,
                10048,
            ):
                print(
                    f"[Debug Server] Port {current_port} occupied, trying {current_port + 1}..."
                )
                current_port += 1
                if current_port > args.port + 10:
                    print(f"[Error] Failed to find available port after 10 retries")
                    exit(1)
                continue
            else:
                print(f"[Error] Failed to start server: {e}")
                exit(1)


if __name__ == "__main__":
    main()
