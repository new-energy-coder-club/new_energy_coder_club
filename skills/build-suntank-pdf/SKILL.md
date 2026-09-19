---
name: build-suntank-pdf
description: 一键构建并质检 SunTank 产品方案 PDF（重新生成插图 → pandoc+xelatex 编译 → 空白页/图片DPI 质检）。当用户要求更新/重建/生成产品方案 PDF、更新插图后同步 PDF、或检查 PDF 质量时使用。
---

# SunTank 产品方案 PDF 构建

将 `docs/*.md` 合订编译为 `build/SunTank-产品方案-V1.1.pdf`，含全部 matplotlib 插图与质检。

## 流程

在项目根目录依次执行：

```bash
python build/build_pdf.py    # 1) 重新生成 7 张插图  2) pandoc+xelatex 编译 PDF
python build/check_pdf.py    # 质检：空白页检测 + 插图有效 DPI（退出码非 0 即失败）
```

两步都成功即完成，向用户报告页数与质检结果。

## 构建脚本要点（build/build_pdf.py 已封装，勿手动改流程）

- **插图**：调 `build/make_figures.py` 生成 fig0_cover ~ fig6_gantt 共 7 张 PNG 到 `build/figures/`
- **编译**：在 `docs/` 目录下跑 pandoc（md 内图片引用是 `../build/figures/...` 相对路径，换目录会丢图）
- **header 处理**：`build/header.tex` 的 `\graphicspath` 是相对路径，而 xelatex 在临时目录工作会找不到封面图 —— 脚本自动生成绝对路径的临时 header 并事后清理，**不要直接改 header.tex 里的 graphicspath**
- **关键 pandoc 参数**：`-s`、`--pdf-engine=xelatex`、`--toc --toc-depth=2`、`--top-level-division=chapter`、`-V classoption=oneside`（**必须保留 oneside**，否则 openright 会在章间插入约 5 页空白页）
- 编译产生的 `input.aux`/`input.log` 由脚本自动清理

## 依赖

- `pandoc`、`xelatex`（TeX Live，字体用 Microsoft YaHei / Segoe UI Emoji）
- Python 包：`matplotlib`（插图）、`pymupdf`（质检）

## 常见问题

| 症状 | 原因 | 处理 |
|---|---|---|
| `Unable to load picture 'fig0_cover.png'` | graphicspath 相对路径失效 | 用 build_pdf.py，不要手工调 pandoc |
| 正文插图变成 alt 文本 | 不在 docs/ 目录下编译 | 同上 |
| PDF 出现多页空白 | 缺 `-V classoption=oneside` | 检查 build_pdf.py 参数是否被改动 |
| 内容/定价/时间线变更 | 源在 docs/*.md 与 build/make_figures.py | 改源文件后重新运行本流程 |
