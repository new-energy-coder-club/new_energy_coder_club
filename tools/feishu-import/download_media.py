#!/usr/bin/env python3
"""Download Feishu document media listed in media-manifest.json."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def safe_name(value: str, fallback: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    value = value.strip("-._")
    return value or fallback


def run(command: list[str], dry_run: bool) -> tuple[bool, str]:
    if dry_run:
        return True, "DRY RUN: " + " ".join(command)
    result = subprocess.run(command, capture_output=True, text=True)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Feishu document media.")
    parser.add_argument("--manifest", required=True, help="Path to media-manifest.json.")
    parser.add_argument("--out", required=True, help="Output media directory.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without downloading.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    media = manifest.get("media", [])
    if not isinstance(media, list):
        print("ERROR: manifest.media must be a list.", file=sys.stderr)
        return 1

    for index, item in enumerate(media, start=1):
        kind = item.get("kind", "media")
        token = item.get("token")
        if not token:
            item["status"] = "failed"
            item["error"] = "missing token"
            continue
        base = safe_name(item.get("name") or item.get("id") or f"media-{index}", f"media-{index}")
        target = out_dir / f"{index:03d}-{kind}-{base}"
        command = [
            "lark-cli",
            "docs",
            "+media-download",
            "--token",
            str(token),
            "--output",
            str(target),
            "--overwrite",
        ]
        if kind == "whiteboard":
            command.extend(["--type", "whiteboard"])
        ok, output = run(command, args.dry_run)
        item["download_command"] = " ".join(command)
        item["status"] = "planned" if args.dry_run and ok else "downloaded" if ok else "failed"
        item["local_path"] = str(target)
        if output:
            item["message"] = output[-1000:]

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "manifest": str(manifest_path), "out": str(out_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
