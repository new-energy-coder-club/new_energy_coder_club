#!/usr/bin/env python3
"""Import top-level Feishu Wiki nodes into NEC Sphinx docs.

Usage:
    python import_wiki_top_level.py \
        --source "https://scn0bdoc8zxg.feishu.cn/wiki/S10LwzVZdiWLwxkEnEqcTcmEn6e" \
        --nodes-json /tmp/nec-wiki-nodes.json \
        --out-dir ../../docs/wiki \
        --static-dir ../../docs/wiki/static
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def run_json(command: list[str]) -> dict:
    """Run a CLI command and parse its JSON output (Windows-compatible)."""
    shell = os.name == "nt"
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=shell,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}\n{result.stderr.strip()}"
        )
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Expected JSON from command: {' '.join(command)}\nOutput begins:\n{stdout[:800]}"
        ) from exc


def fetch_document(obj_token: str, title_hint: str = "", limit: int = 5000) -> tuple[str, str]:
    """Fetch a single docx document via lark-cli docs +fetch."""
    chunks: list[str] = []
    title = title_hint or "Untitled"
    offset = 0
    while True:
        data = run_json(
            [
                "lark-cli",
                "docs",
                "+fetch",
                "--doc",
                obj_token,
                "--format",
                "json",
                "--offset",
                str(offset),
                "--limit",
                str(limit),
            ]
        )
        payload = data.get("data", data)
        title = payload.get("title") or title
        markdown = payload.get("markdown") or payload.get("content") or ""
        if markdown and (not chunks or markdown != chunks[-1]):
            chunks.append(markdown)
        if not payload.get("has_more"):
            break
        offset += limit
    return title, "\n\n".join(chunks).strip()


def slugify(value: str) -> str:
    """Create a safe filename slug from a title."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = value.strip("-")
    return value


def clean_title(title: str) -> str:
    """Remove decorative brackets from titles."""
    title = title.strip()
    title = re.sub(r"^[<\[(\s]+|[>\])\s]+$", "", title)
    return title.strip()


def download_media(markdown: str, static_dir: Path) -> str:
    """Download <image> tags and rewrite URLs to relative paths.

    This is a simple placeholder implementation. For full media support,
    use lark-cli drive/media download commands.
    """
    # Keep markdown as-is for now; media download can be added later.
    return markdown


def write_markdown(out_dir: Path, filename: str, title: str, markdown: str) -> Path:
    """Write a Markdown file, avoiding duplicate top-level headings."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    # lark-cli already includes a level-1 heading from the document title.
    stripped = markdown.strip()
    if stripped.startswith(f"# {title}") or stripped.startswith(f"# {title.strip()}"):
        content = stripped
    else:
        content = f"# {title}\n\n{markdown}"
    path.write_text(content, encoding="utf-8")
    return path


def token_from_url(source: str) -> str:
    parsed = urlparse(source)
    parts = [p for p in parsed.path.split("/") if p]
    for marker in ("wiki", "docx", "doc"):
        if marker in parts:
            idx = parts.index(marker)
            if idx + 1 < len(parts):
                return parts[idx + 1]
    return source.strip()


def fetch_wiki_root(source: str) -> tuple[str, str]:
    """Fetch the root wiki node document."""
    token = token_from_url(source)
    data = run_json(
        [
            "lark-cli",
            "wiki",
            "spaces",
            "get_node",
            "--params",
            json.dumps({"token": token}, ensure_ascii=False),
        ]
    )
    node = data.get("data", {}).get("node") or data.get("node")
    if not isinstance(node, dict):
        raise RuntimeError("Unable to find root wiki node.")
    title = node.get("title", "Wiki Home")
    obj_token = node.get("obj_token", "")
    if not obj_token:
        raise RuntimeError("Root wiki node has no obj_token.")
    doc_title, markdown = fetch_document(obj_token, title)
    return doc_title, markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Import top-level Feishu Wiki nodes into NEC docs.")
    parser.add_argument("--source", required=True, help="Wiki URL.")
    parser.add_argument("--nodes-json", required=True, help="JSON file from lark-cli wiki +node-list.")
    parser.add_argument("--out-dir", required=True, help="Output directory for Markdown files.")
    parser.add_argument("--static-dir", help="Static/media output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    nodes_path = Path(args.nodes_json).expanduser().resolve()
    nodes_data = json.loads(nodes_path.read_text(encoding="utf-8"))
    nodes = nodes_data.get("data", {}).get("nodes", [])

    written: list[tuple[str, str]] = []  # (filename, title)

    # Root document is always index 10 to match existing NEC docs convention
    try:
        root_title, root_md = fetch_wiki_root(args.source)
        root_file = "10_NEC知识库_首页.md"
        write_markdown(out_dir, root_file, root_title, root_md)
        written.append((root_file, root_title))
        print(f"Wrote root: {root_file}")
    except Exception as exc:
        print(f"ERROR fetching root: {exc}", file=sys.stderr)

    # Top-level child documents (01-09)
    for index, node in enumerate(nodes, start=1):
        title = clean_title(node.get("title", f"Document {index}"))
        obj_token = node.get("obj_token", "")
        if not obj_token:
            print(f"Skipping node without obj_token: {title}")
            continue
        try:
            doc_title, md = fetch_document(obj_token, title)
            # Keep stable filenames aligned with existing NEC docs naming
            slug = slugify(doc_title) or f"doc-{index}"
            filename = f"{index:02d}_{slug}.md"
            write_markdown(out_dir, filename, doc_title, md)
            written.append((filename, doc_title))
            print(f"Wrote: {filename} ({doc_title})")
        except Exception as exc:
            print(f"ERROR fetching {title}: {exc}", file=sys.stderr)

    # Write/update README index
    readme_lines = [
        "# NEC 知识库导出文档索引",
        "",
        f"> 导出时间：2026-06-22",
        f"> 来源：{args.source}",
        "",
        "## 文档清单",
        "",
        "| 序号 | 文件名 | 标题 |",
        "|:----:|--------|------|",
    ]
    for idx, (filename, title) in enumerate(written, start=1):
        readme_lines.append(f"| {idx:02d} | `{filename}` | {title} |")
    readme_lines.extend([
        "",
        "---",
        "",
        "*由 feishu-doc-webify + NEC docs 导入脚本生成*",
        "",
    ])
    (out_dir / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")

    print(f"\nDone. Wrote {len(written)} documents to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
