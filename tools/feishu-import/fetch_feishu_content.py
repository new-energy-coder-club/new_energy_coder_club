#!/usr/bin/env python3
"""Fetch Feishu/Lark document or Wiki content into a normalized JSON bundle."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse


MEDIA_TAG_RE = re.compile(r"<(image|file|whiteboard)\b([^>]*)/?>", re.IGNORECASE)
ATTR_RE = re.compile(r'([A-Za-z_:-]+)="([^"]*)"')
SUPPORTED_DOC_TYPES = {"doc", "docx"}
UNSUPPORTED_TYPES = {"sheet", "bitable", "slides", "file", "mindnote"}


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def run_json(command: list[str]) -> dict:
    # Windows: lark-cli is installed as a .CMD wrapper; subprocess needs
    # shell=True to execute it and UTF-8 encoding to read its output.
    import os

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
            "Command failed: {}\n{}".format(" ".join(command), result.stderr.strip())
        )
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Expected JSON from command: {}\nOutput begins:\n{}".format(
                " ".join(command), stdout[:800]
            )
        ) from exc


def token_from_source(source: str, preferred: str | None = None) -> str:
    parsed = urlparse(source)
    if parsed.scheme and parsed.netloc:
        parts = [part for part in parsed.path.split("/") if part]
        for marker in ([preferred] if preferred else ["wiki", "docx", "doc"]):
            if marker in parts:
                index = parts.index(marker)
                if index + 1 < len(parts):
                    return parts[index + 1]
        if parts:
            return parts[-1]
    return source.strip()


def get_nested(data: dict, *keys: str):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def unwrap_node(data: dict) -> dict:
    node = get_nested(data, "data", "node") or data.get("node")
    if not isinstance(node, dict):
        raise RuntimeError("Unable to find node in wiki response.")
    return node


def slugify(value: str, fallback: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or fallback


def unique_slug(title: str, seen: set[str], fallback: str) -> str:
    base = slugify(title, fallback)
    slug = base
    counter = 2
    while slug in seen:
        slug = f"{base}-{counter}"
        counter += 1
    seen.add(slug)
    return slug


def normalize_fetch_response(data: dict, title_hint: str | None = None) -> tuple[str, str, bool]:
    payload = data.get("data") if isinstance(data.get("data"), dict) else data
    title = (
        payload.get("title")
        or payload.get("document", {}).get("title")
        or title_hint
        or "Untitled Feishu Document"
    )
    markdown = (
        payload.get("markdown")
        or payload.get("content")
        or payload.get("text")
        or payload.get("document", {}).get("markdown")
        or ""
    )
    has_more = bool(payload.get("has_more") or payload.get("hasMore"))
    return str(title), str(markdown), has_more


def fetch_document(doc_ref: str, title_hint: str | None = None, limit: int = 5000) -> tuple[str, str]:
    chunks: list[str] = []
    title = title_hint or "Untitled Feishu Document"
    offset = 0
    while True:
        command = [
            "lark-cli",
            "docs",
            "+fetch",
            "--doc",
            doc_ref,
            "--format",
            "json",
            "--offset",
            str(offset),
            "--limit",
            str(limit),
        ]
        data = run_json(command)
        title, markdown, has_more = normalize_fetch_response(data, title)
        if markdown and (not chunks or markdown != chunks[-1]):
            chunks.append(markdown)
        if not has_more:
            break
        offset += limit
    return title, "\n\n".join(chunks).strip()


def resolve_wiki_node(source: str) -> dict:
    token = token_from_source(source, "wiki")
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
    return unwrap_node(data)


def list_wiki_children(space_id: str, parent_node_token: str, delay: float = 0.15) -> list[dict]:
    items: list[dict] = []
    page_token = ""
    while True:
        command = [
            "lark-cli",
            "wiki",
            "+node-list",
            "--space-id",
            space_id,
            "--parent-node-token",
            parent_node_token,
            "--page-size",
            "50",
        ]
        if page_token:
            command.extend(["--page-token", page_token])
        data = run_json(command)
        payload = data.get("data", {})
        batch = payload.get("nodes") or []
        if isinstance(batch, list):
            items.extend(batch)
        if not payload.get("has_more"):
            break
        page_token = str(payload.get("page_token") or "")
        if not page_token:
            break
        time.sleep(delay)
    return items


def parse_attrs(raw: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in ATTR_RE.finditer(raw)}


def extract_media(markdown: str, doc_id: str, doc_title: str) -> list[dict]:
    media: list[dict] = []
    for index, match in enumerate(MEDIA_TAG_RE.finditer(markdown), start=1):
        kind = match.group(1).lower()
        attrs = parse_attrs(match.group(2))
        token = attrs.get("token")
        if not token:
            continue
        media.append(
            {
                "id": f"{doc_id}-media-{index}",
                "doc_id": doc_id,
                "doc_title": doc_title,
                "kind": kind,
                "token": token,
                "name": attrs.get("name") or f"{kind}-{index}",
                "width": attrs.get("width"),
                "height": attrs.get("height"),
                "align": attrs.get("align"),
                "status": "pending",
            }
        )
    return media


def doc_from_node(node: dict, seen: set[str], index: int) -> tuple[dict | None, dict | None]:
    obj_type = str(node.get("obj_type") or "")
    title_hint = str(node.get("title") or f"Document {index}")
    if obj_type not in SUPPORTED_DOC_TYPES:
        return None, {
            "title": title_hint,
            "obj_type": obj_type or "unknown",
            "node_token": node.get("node_token"),
            "obj_token": node.get("obj_token"),
            "reason": "unsupported object type",
        }
    obj_token = str(node.get("obj_token") or "")
    if not obj_token:
        return None, {
            "title": title_hint,
            "obj_type": obj_type,
            "node_token": node.get("node_token"),
            "reason": "missing obj_token",
        }
    title, markdown = fetch_document(obj_token, title_hint)
    slug = unique_slug(title, seen, f"doc-{index}")
    doc = {
        "id": slug,
        "slug": slug,
        "title": title,
        "markdown": markdown,
        "obj_type": obj_type,
        "obj_token": obj_token,
        "node_token": node.get("node_token"),
        "parent_node_token": node.get("parent_node_token"),
        "source": "wiki",
    }
    return doc, None


def build_single(source: str, seen: set[str]) -> tuple[list[dict], list[dict], dict]:
    source_token_type = "wiki" if "/wiki/" in source else None
    metadata: dict[str, object] = {"scope": "single", "source": source}
    doc_ref = source
    obj_type = "docx" if "/docx/" in source else "doc" if "/doc/" in source else "doc"

    if source_token_type == "wiki":
        node = resolve_wiki_node(source)
        metadata["root_node"] = node
        obj_type = str(node.get("obj_type") or "")
        if obj_type not in SUPPORTED_DOC_TYPES:
            skipped = [
                {
                    "title": node.get("title"),
                    "obj_type": obj_type,
                    "node_token": node.get("node_token"),
                    "obj_token": node.get("obj_token"),
                    "reason": "unsupported root object type",
                }
            ]
            return [], skipped, metadata
        doc_ref = str(node.get("obj_token") or source)

    title, markdown = fetch_document(doc_ref)
    slug = unique_slug(title, seen, "index")
    doc = {
        "id": slug,
        "slug": slug,
        "title": title,
        "markdown": markdown,
        "obj_type": obj_type,
        "obj_token": token_from_source(doc_ref),
        "source": source,
    }
    return [doc], [], metadata


def build_wiki(source: str, seen: set[str]) -> tuple[list[dict], list[dict], dict]:
    root = resolve_wiki_node(source)
    space_id = str(root.get("space_id") or root.get("origin_space_id") or "")
    root_token = str(root.get("node_token") or token_from_source(source, "wiki"))
    if not space_id:
        raise RuntimeError("Wiki node response did not include space_id.")

    metadata: dict[str, object] = {
        "scope": "wiki",
        "source": source,
        "space_id": space_id,
        "root_node": root,
    }
    docs: list[dict] = []
    skipped: list[dict] = []

    root_doc, root_skip = doc_from_node(root, seen, 1)
    if root_doc:
        root_doc["is_root"] = True
        docs.append(root_doc)
    if root_skip:
        skipped.append(root_skip)

    queue = [root_token]
    visited = {root_token}
    index = 2
    while queue:
        parent = queue.pop(0)
        for child in list_wiki_children(space_id, parent):
            node_token = str(child.get("node_token") or "")
            doc, skip = doc_from_node(child, seen, index)
            if doc:
                docs.append(doc)
                index += 1
            if skip:
                skipped.append(skip)
            if child.get("has_child") and node_token and node_token not in visited:
                visited.add(node_token)
                queue.append(node_token)
    return docs, skipped, metadata


def write_bundle(out_dir: Path, source: str, scope: str, docs: list[dict], skipped: list[dict], metadata: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    all_media: list[dict] = []
    for doc in docs:
        all_media.extend(extract_media(doc.get("markdown", ""), doc["id"], doc["title"]))

    content = {
        "version": 1,
        "source": source,
        "scope": scope,
        "title": docs[0]["title"] if len(docs) == 1 else metadata.get("root_node", {}).get("title", "Feishu Knowledge Site"),
        "docs": docs,
        "media": all_media,
        "skipped_nodes": skipped,
        "metadata": metadata,
    }
    media_manifest = {"version": 1, "source": source, "media": all_media}
    report = {
        "source": source,
        "scope": scope,
        "docs_count": len(docs),
        "media_count": len(all_media),
        "media_by_type": {
            kind: sum(1 for item in all_media if item["kind"] == kind)
            for kind in ["image", "file", "whiteboard"]
        },
        "skipped_nodes": skipped,
    }

    (out_dir / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "media-manifest.json").write_text(json.dumps(media_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "fetch-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def build_from_mock(mock_doc_json: Path, source: str, seen: set[str]) -> tuple[list[dict], list[dict], dict]:
    data = json.loads(mock_doc_json.read_text(encoding="utf-8"))
    title, markdown, _ = normalize_fetch_response(data)
    slug = unique_slug(title, seen, "index")
    doc = {
        "id": slug,
        "slug": slug,
        "title": title,
        "markdown": markdown,
        "obj_type": "docx",
        "obj_token": "mock",
        "source": source,
    }
    return [doc], [], {"scope": "single", "source": source, "mock": True}


def build_wiki_from_mock(mock_wiki_json: Path, source: str, seen: set[str]) -> tuple[list[dict], list[dict], dict]:
    data = json.loads(mock_wiki_json.read_text(encoding="utf-8"))
    root = data["root"]
    children = data.get("children", {})
    documents = data.get("documents", {})
    docs: list[dict] = []
    skipped: list[dict] = []
    queue = [root]
    index = 1

    while queue:
        node = queue.pop(0)
        obj_type = str(node.get("obj_type") or "")
        title = str(node.get("title") or f"Document {index}")
        obj_token = str(node.get("obj_token") or "")
        if obj_type in SUPPORTED_DOC_TYPES and obj_token in documents:
            payload = documents[obj_token]
            doc_title = str(payload.get("title") or title)
            slug = unique_slug(doc_title, seen, f"doc-{index}")
            docs.append(
                {
                    "id": slug,
                    "slug": slug,
                    "title": doc_title,
                    "markdown": str(payload.get("markdown") or ""),
                    "obj_type": obj_type,
                    "obj_token": obj_token,
                    "node_token": node.get("node_token"),
                    "parent_node_token": node.get("parent_node_token"),
                    "source": "wiki",
                    "is_root": node is root,
                }
            )
            index += 1
        else:
            skipped.append(
                {
                    "title": title,
                    "obj_type": obj_type or "unknown",
                    "node_token": node.get("node_token"),
                    "obj_token": obj_token,
                    "reason": "unsupported object type" if obj_type not in SUPPORTED_DOC_TYPES else "missing mock document",
                }
            )
        queue.extend(children.get(node.get("node_token"), []))

    return docs, skipped, {"scope": "wiki", "source": source, "mock": True, "root_node": root}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Feishu document or Wiki content.")
    parser.add_argument("--source", required=True, help="Feishu docx/doc/wiki URL or token.")
    parser.add_argument("--scope", required=True, choices=["single", "wiki"], help="Fetch one document or a Wiki subtree.")
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument("--mock-doc-json", help="Test helper: use a saved docs +fetch JSON response.")
    parser.add_argument("--mock-wiki-json", help="Test helper: use a saved Wiki tree fixture.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out).expanduser().resolve()
    seen: set[str] = set()

    try:
        if args.mock_doc_json:
            docs, skipped, metadata = build_from_mock(Path(args.mock_doc_json), args.source, seen)
        elif args.mock_wiki_json:
            docs, skipped, metadata = build_wiki_from_mock(Path(args.mock_wiki_json), args.source, seen)
        elif args.scope == "single":
            docs, skipped, metadata = build_single(args.source, seen)
        else:
            docs, skipped, metadata = build_wiki(args.source, seen)
        write_bundle(out_dir, args.source, args.scope, docs, skipped, metadata)
    except Exception as exc:
        eprint(f"ERROR: {exc}")
        return 1

    report_path = out_dir / "fetch-report.json"
    print(json.dumps({"ok": True, "out": str(out_dir), "report": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
