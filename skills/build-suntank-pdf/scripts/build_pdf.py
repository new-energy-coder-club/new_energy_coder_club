# -*- coding: utf-8 -*-
# SunTank 产品方案 PDF 一键构建
# 用法: python build/build_pdf.py
# 步骤: 1) 重新生成全部插图  2) pandoc + xelatex 编译 PDF
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
DOCS = os.path.join(ROOT, "docs")
OUT_PDF = os.path.join(BUILD, "SunTank-产品方案-V1.1.pdf")

DOCS_MD = [
    "00-产品方案总索引.md",
    "01-市场研究与竞品分析.md",
    "02-PRD-产品需求文档.md",
    "03-产品构思与技术方案.md",
    "04-商业模式与GTM.md",
    "05-风险与路线图.md",
    "06-硬件清单与成本速查表.md",
]

def run(cmd, cwd=None):
    print(">>", " ".join(cmd) if isinstance(cmd, list) else cmd)
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        sys.exit("FAILED (exit %d)" % r.returncode)

# ---------- 1. 生成插图 ----------
print("=== [1/2] 生成插图 ===")
run([sys.executable, os.path.join(BUILD, "make_figures.py")], cwd=ROOT)

# ---------- 2. 编译 PDF ----------
print("=== [2/2] 编译 PDF ===")

# header.tex 中 \graphicspath 是相对路径，xelatex 在临时目录工作会找不到封面图，
# 这里生成一个带绝对路径的临时 header
with open(os.path.join(BUILD, "header.tex"), encoding="utf-8") as f:
    header = f.read()
fig_dir = os.path.join(BUILD, "figures").replace("\\", "/")
header_abs = header.replace(
    r"\graphicspath{{build/}{build/figures/}}",
    r"\graphicspath{{%s/}}" % fig_dir,
)
if header_abs == header:
    print("!! 警告: header.tex 中未找到 graphicspath 行，封面图可能丢失")
tmp_header = os.path.join(BUILD, "_header_build.tex")
with open(tmp_header, "w", encoding="utf-8") as f:
    f.write(header_abs)

try:
    run([
        "pandoc", *DOCS_MD,
        "-s",
        "-o", OUT_PDF,
        "--pdf-engine=xelatex",
        "-H", tmp_header,
        "--metadata", "title=SunTank 日光冰罐 · 产品方案",
        "--metadata", "author=产品组",
        "--toc", "--toc-depth=2",
        "--top-level-division=chapter",
        "-V", "classoption=oneside",  # 章节可从任意页开始，避免 openright 插入空白页
    ], cwd=DOCS)
finally:
    # 清理临时文件
    for p in [tmp_header,
              os.path.join(BUILD, "input.aux"),
              os.path.join(BUILD, "input.log")]:
        if os.path.exists(p):
            os.remove(p)

print("=== 完成: %s ===" % OUT_PDF)
