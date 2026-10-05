# -*- coding: utf-8 -*-
"""NEC 资料发布管线：PDF/Excel/二进制 -> R2 CDN + 原文原图 MDX 页面。

用法：
  1. 把附件复制到本脚本所在目录（staging）；
  2. 编辑下方 RESOURCES 清单与常量（TOPIC、DOCS_DIR 等）；
  3. 用含 boto3 + pymupdf 的 Python 运行：
     ~/.kimi/skills/r2-image-sync/.venv/Scripts/python.exe publish_resources.py

R2 密钥自动从 ~/.kimi/skills/r2-image-sync/r2_image_sync.py 读取（正则提取），
找不到时回退环境变量。密钥严禁写入本文件或提交 git。
"""
import hashlib
import os
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

# ============================ 资源配置 ============================
STAGING = Path(__file__).parent.resolve()
DOCS_DIR = Path.home() / "Documents" / "kimi" / "workspace" / "nec-docs" / "mechanical"
TOPIC = "mech-training"          # R2 路径 files/<topic>/...
IMG_WIDTH = 1600                 # 整页渲染目标宽度(px)

RESOURCES = [
    # 示例：PDF（原文 + 原位插图；page_only 整页渲染矢量图页）
    # {
    #     "file": "RM M2006 电机说明.pdf",
    #     "slug": "robomaster-m2006-p36-motor-guide",
    #     "mdx": "m2006-motor-guide",
    #     "title": "RoboMaster M2006 P36 电机使用说明",
    #     "description": "DJI RoboMaster M2006 P36 直流无刷减速电机官方使用说明（原文）",
    #     "size": "0.7 MB",
    #     "type": "pdf",
    #     "page_only": {1, 4, 5, 6, 7},
    #     "page_also": set(),
    # },
    # 示例：Excel（全量转 Markdown 表格）
    # {
    #     "file": "供应商名录.xlsx",
    #     "slug": "rm-rc-supplier-directory",
    #     "mdx": "rm-rc-supplier-directory",
    #     "title": "RM / RC 供应商名录",
    #     "description": "常用供应商的质量、交货、发票、价格与真实评价",
    #     "size": "0.2 MB",
    #     "type": "xlsx",
    # },
    # 示例：二进制（仅上传 + 下载页）
    # {"file": "demo.zip", "slug": "demo-pack", "mdx": "demo-pack",
    #  "title": "演示资料包", "description": "……", "size": "1.0 MB", "type": "binary"},
]

# ========================== R2 配置读取 ==========================

def load_r2_config():
    local = Path.home() / ".kimi" / "skills" / "r2-image-sync" / "r2_image_sync.py"
    cfg = {}
    if local.exists():
        text = local.read_text(encoding="utf-8")
        for k in ["R2_ENDPOINT", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY",
                  "R2_BUCKET", "R2_CDN_BASE_URL"]:
            m = re.search(rf'{k}\s*=\s*"([^"]+)"', text)
            if m:
                cfg[k] = m.group(1)
    for k in ["R2_ENDPOINT", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY",
              "R2_BUCKET", "R2_CDN_BASE_URL"]:
        cfg.setdefault(k, os.environ.get(k, ""))
    missing = [k for k, v in cfg.items() if not v]
    if missing:
        sys.exit(f"[FATAL] 缺少 R2 配置: {missing}（本地 r2-image-sync 与环境变量均未找到）")
    return cfg


CFG = load_r2_config()

import boto3  # noqa: E402
from botocore.config import Config  # noqa: E402

s3 = boto3.client("s3", endpoint_url=CFG["R2_ENDPOINT"],
                  aws_access_key_id=CFG["R2_ACCESS_KEY_ID"],
                  aws_secret_access_key=CFG["R2_SECRET_ACCESS_KEY"],
                  region_name="auto", config=Config(signature_version="s3v4"))
CDN = CFG["R2_CDN_BASE_URL"]
BUCKET = CFG["R2_BUCKET"]

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def collect_existing(prefix):
    keys = set()
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    while True:
        keys.update(o["Key"] for o in resp.get("Contents", []))
        if not resp.get("IsTruncated"):
            break
        resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix,
                                  ContinuationToken=resp["NextContinuationToken"])
    return keys


EXISTING = collect_existing(f"files/{TOPIC}/")

MIME = {
    ".pdf": "application/pdf",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".zip": "application/zip", ".rar": "application/x-rar-compressed",
}


def upload(local: Path, key: str, ct: str = None) -> str:
    url = f"{CDN}/{key}"
    if key not in EXISTING:
        ct = ct or MIME.get(local.suffix.lower(), "application/octet-stream")
        s3.upload_file(str(local), BUCKET, key, ExtraArgs={"ContentType": ct})
        EXISTING.add(key)
        print(f"[UPLOAD] {key} ({local.stat().st_size//1024} KB)")
    return url

# ============================ 文本工具 ============================


def esc(t: str) -> str:
    return (t.replace("\\", "\\\\").replace("<", "\\<").replace(">", "\\>")
             .replace("{", "\\{").replace("}", "\\}"))


def join_lines(lines):
    out = ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if not out:
            out = ln
        elif (out[-1].isascii() and out[-1].isalnum()) and (ln[0].isascii() and ln[0].isalnum()):
            out += " " + ln
        else:
            out += ln
    return out


def garble_ratio(text: str) -> float:
    if not text.strip():
        return 0.0
    bad = total = 0
    for ch in text:
        o = ord(ch)
        if ch.isspace():
            continue
        total += 1
        if (0x0370 <= o <= 0x04FF or 0x0B80 <= o <= 0x0BFF or 0x0F00 <= o <= 0x0FFF
                or 0xE000 <= o <= 0xF8FF or o == 0xFFFD or 0x0250 <= o <= 0x02FF):
            bad += 1
    return bad / max(total, 1)

# ============================ PDF 处理 ============================


def render_page(page, local: Path, width: int = IMG_WIDTH):
    import fitz
    zoom = width / page.rect.width
    page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(str(local))


def build_pdf(res) -> str:
    import fitz
    slug = res["slug"]
    page_only = set(res.get("page_only", set()))
    page_also = set(res.get("page_also", set()))
    img_dir = STAGING / "images" / slug
    img_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(STAGING / res["file"]))
    parts, seen, n_img = [], {}, 0

    for pno, page in enumerate(doc, 1):
        page_text = page.get_text("text")
        garbled = garble_ratio(page_text) > 0.15 and len(page_text.strip()) > 50
        if pno in page_only or (garbled and pno not in page_also):
            local = img_dir / f"p{pno:02d}-full.png"
            if not local.exists():
                render_page(page, local)
            url = upload(local, f"files/{TOPIC}/images/{slug}/p{pno:02d}-full.png", "image/png")
            parts.append(f"![原文第 {pno} 页]({url})")
            continue

        items = []
        for b in page.get_text("dict")["blocks"]:
            y, x = round(b["bbox"][1]), round(b["bbox"][0])
            if b["type"] == 0:
                lines = ["".join(s["text"] for s in l.get("spans", []))
                         for l in b.get("lines", [])]
                text = join_lines([l for l in lines if l.strip()])
                if text:
                    items.append((y, x, "text", text))
            elif b["type"] == 1:
                ib, ext = b.get("image"), b.get("ext", "png")
                w = b["bbox"][2] - b["bbox"][0]
                h = b["bbox"][3] - b["bbox"][1]
                if ib and len(ib) > 3000 and w > 40 and h > 40:
                    items.append((y, x, "image", (ib, ext)))
        items.sort(key=lambda t: (t[0], t[1]))

        for _, _, kind, payload in items:
            if kind == "text":
                parts.append(esc(payload))
            else:
                ib, ext = payload
                h = hashlib.md5(ib).hexdigest()
                if h in seen:
                    continue
                n_img += 1
                fname = f"p{pno:02d}-img{n_img:02d}.{ext}"
                local = img_dir / fname
                if not local.exists():
                    local.write_bytes(ib)
                ct = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
                url = upload(local, f"files/{TOPIC}/images/{slug}/{fname}", ct)
                seen[h] = url
                parts.append(f"![{res['title']} 插图]({url})")

        if pno in page_also:
            local = img_dir / f"p{pno:02d}-full.png"
            if not local.exists():
                render_page(page, local)
            url = upload(local, f"files/{TOPIC}/images/{slug}/p{pno:02d}-full.png", "image/png")
            parts.append("本页原图（含矢量图示）：")
            parts.append(f"![原文第 {pno} 页]({url})")

    doc.close()
    print(f"[PDF] {slug}: {n_img} inline images")
    return "\n\n".join(parts)

# ============================ XLSX 处理 ============================

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_xlsx_raw(path: Path):
    """跳过样式表的裸 XML 读取（规避 openpyxl 对飞书/WPS 导出文件的 Fill 报错）。"""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rels}
    RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    sheets = {}
    for sh in wb.find("m:sheets", NS):
        target = rid2t[sh.get(RID)]
        if not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        root = ET.fromstring(z.read(target))
        rows = []
        for row in root.iter("{%s}row" % NS["m"]):
            cells = {}
            for c in row.findall("m:c", NS):
                ref = c.get("r", "A")
                col = re.match(r"[A-Z]+", ref).group(0)
                idx = 0
                for ch in col:
                    idx = idx * 26 + (ord(ch) - 64)
                idx -= 1
                v = c.find("m:v", NS)
                is_el = c.find("m:is", NS)
                if c.get("t") == "s" and v is not None:
                    val = shared[int(v.text)]
                elif c.get("t") == "inlineStr" and is_el is not None:
                    val = "".join(t.text or "" for t in is_el.iter("{%s}t" % NS["m"]))
                elif v is not None:
                    val = v.text
                else:
                    val = ""
                cells[idx] = val
            if cells and any(str(v).strip() for v in cells.values()):
                rows.append(cells)
        sheets[sh.get("name")] = rows
    return sheets


def cell_mdx(text) -> str:
    t = str(text).strip()
    t = re.sub(r"\s*\n\s*", "<br/>", t)
    t = t.replace("|", "\\|").replace("{", "\\{").replace("}", "\\}")
    if re.fullmatch(r"https?://\S+", t):
        return f"[打开链接]({t})"
    return t


def sheet_to_md(rows, first_header="名称") -> str:
    max_col = max((max(r.keys()) for r in rows), default=-1)
    used = [i for i in range(max_col + 1) if any(str(r.get(i, "")).strip() for r in rows)]
    if not used:
        return ""
    header, head, extra = rows[0], [], 0
    for i in used:
        h = str(header.get(i, "")).strip()
        if not h:
            h = first_header if i == used[0] else f"补充{(extra := extra + 1)}"
        head.append(h.replace("|", "\\|"))
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows[1:]:
        lines.append("| " + " | ".join(cell_mdx(r.get(i, "")) for i in used) + " |")
    return "\n".join(lines)


def build_xlsx(res) -> str:
    sheets = read_xlsx_raw(STAGING / res["file"])
    parts = []
    for name, rows in sheets.items():
        parts.append(f"## {name}\n")
        parts.append(sheet_to_md(rows))
    print(f"[XLSX] {res['slug']}: {len(sheets)} sheets")
    return "\n\n".join(parts)

# ============================ 主流程 ============================

INTRO = {
    "pdf": "以下为文档原文内容；含矢量图示或提取乱码的页面以整页原图展示：",
    "xlsx": "以下为表格全部内容，按 Sheet 分类展示：",
    "binary": "该资源为二进制文件，请下载后使用：",
}


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    if not RESOURCES:
        sys.exit("[FATAL] RESOURCES 为空，请先编辑脚本顶部资源清单")
    for res in RESOURCES:
        src = STAGING / res["file"]
        if not src.exists():
            print(f"[SKIP] 文件不存在: {src}")
            continue
        dl_url = upload(src, f"files/{TOPIC}/{res['slug']}{src.suffix.lower()}")
        rtype = res.get("type", "pdf")
        if rtype == "pdf":
            body = build_pdf(res)
        elif rtype == "xlsx":
            body = build_xlsx(res)
        else:
            body = ""
        mdx = f"""---
title: "{res['title']}"
description: "{res['description']}"
---

[下载原始文件（{res.get('size', '')}）]({dl_url})

{INTRO.get(rtype, '')}

{body}

## 相关页面

- [机械组培训资料下载](/mechanical/training-resources)
- [机构设计概述](/mechanical/introduction)
"""
        out = DOCS_DIR / f"{res['mdx']}.mdx"
        out.write_text(mdx, encoding="utf-8")
        print(f"[MDX] {out.name}: {len(mdx)} chars")
    print("PUBLISH DONE")


if __name__ == "__main__":
    main()
