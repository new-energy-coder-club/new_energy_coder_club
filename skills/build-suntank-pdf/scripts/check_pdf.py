# -*- coding: utf-8 -*-
# SunTank PDF 质检：空白页检测 + 插图可读性（有效 DPI）检查
# 用法: python build/check_pdf.py
# 退出码: 0 = 通过；1 = 发现问题
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "SunTank-产品方案-V1.1.pdf")

MIN_DPI = 150          # 印刷可读下限
EXPECTED_IMAGES = 7    # 封面 fig0 + 正文 fig1-fig6

def main():
    try:
        import fitz
    except ImportError:
        sys.exit("需要 pymupdf: pip install pymupdf")
    if not os.path.exists(PDF):
        sys.exit("PDF 不存在: %s （先运行 python build/build_pdf.py）" % PDF)

    d = fitz.open(PDF)
    print("PDF: %s (%d 页)" % (PDF, d.page_count))
    problems = []

    # ---------- 1. 空白页 ----------
    blanks = []
    for p in d:
        text = p.get_text().strip()
        imgs = p.get_images()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        # 剔除页眉页脚后判断正文
        body = [l for l in lines
                if "SunTank" not in l and "2026-08" not in l
                and not (l.startswith("—") and l.endswith("—"))]
        if not body and not imgs:
            blanks.append(p.number + 1)
    if blanks:
        problems.append("空白页: %s" % blanks)
    else:
        print("[OK] 无空白页")

    # ---------- 2. 插图数量与有效 DPI ----------
    img_count = 0
    for p in d:
        for img in p.get_images(full=True):
            xref = img[0]
            info = d.extract_image(xref)
            for r in p.get_image_rects(xref):
                img_count += 1
                dpi_x = info["width"] / (r.width / 72) if r.width else 0
                dpi_y = info["height"] / (r.height / 72) if r.height else 0
                status = "OK" if min(dpi_x, dpi_y) >= MIN_DPI else "LOW-DPI"
                print("  p%-3d %dx%dpx 有效DPI %.0fx%.0f  %s"
                      % (p.number + 1, info["width"], info["height"], dpi_x, dpi_y, status))
                if status != "OK":
                    problems.append("p%d 图片 DPI 过低 (%.0f)" % (p.number + 1, min(dpi_x, dpi_y)))
    if img_count < EXPECTED_IMAGES:
        problems.append("插图数量不足: %d/%d" % (img_count, EXPECTED_IMAGES))
    else:
        print("[OK] 插图数量 %d/%d" % (img_count, EXPECTED_IMAGES))

    # ---------- 结论 ----------
    if problems:
        print("\n质检未通过:")
        for x in problems:
            print("  -", x)
        sys.exit(1)
    print("\n质检通过 ✓")

if __name__ == "__main__":
    main()
