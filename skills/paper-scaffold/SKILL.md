---
name: paper-scaffold
description: 论文项目目录标准化工具。对现有论文目录进行体检和整理，或从零创建新论文项目结构。支持三种模板：CIT毕业设计（ctexbook）、国际会议/期刊（ICML/IEEE/NeurIPS 等 article 类）、通用学术论文。用户提到"新建论文""论文目录整理""paper 结构""scaffold paper""初始化论文项目"时使用。
---

# paper-scaffold — 论文目录标准化

## 职责

1. **audit**：体检现有论文目录，报告违反标准结构的问题
2. **init**：从零创建标准目录骨架 + 必要文件
3. **fix**：对现有目录执行整理（移动文件、创建 .gitignore、归档产物）

## 触发方式

```
/paper-scaffold [子命令] [路径] [--type TYPE]
```

- 子命令省略 → 自动 **audit** 当前目录或指定路径
- `--type`：`cit`（默认，常州工学院毕业设计）| `icml` | `ieee` | `generic`

---

## 标准目录结构

所有类型共享同一骨架，差异仅在模板文件内容：

```
<paper-root>/
├── main.tex              # 主稿入口（单一 .tex 入口，不重名）
├── refs.bib              # 参考文献（BibTeX，禁止 thebibliography 手写）
├── .gitignore            # 排除编译产物、scratch/、drafts/
│
├── images/               # 正文引用的全部图片（唯一图片目录）
│   └── .gitkeep
│
├── sections/             # 各章节独立 .tex（\input 进 main.tex）
│   └── .gitkeep
│
├── scripts/              # 辅助脚本
│   ├── fix/              # fix_*.py — 格式修复类
│   ├── plot/             # 绘图、图表生成类
│   └── tmp/              # 临时调试脚本（.gitignore 排除）
│
├── build/                # 编译产物（.gitignore 排除）
│   └── .gitkeep
│
├── drafts/               # 草稿文本、中间产物（.gitignore 排除）
│   └── .gitkeep
│
├── scratch/              # 调试用 test_*.tex（.gitignore 排除）
│   └── .gitkeep
│
└── archive/              # 旧版本、备份
    └── .gitkeep
```

### CIT 类型额外文件

```
├── main.tex              # \documentclass[zihao=-4,...]{ctexbook}
├── Logo.png              # 学校 Logo（封面用）
└── CIT_name.pdf          # 学校名称 PDF 图（封面用）
```

### ICML/IEEE 类型额外文件

```
├── main.tex              # \documentclass{article} + 会议 sty
├── *.sty / *.bst         # 会议样式文件（保留根目录）
└── supplement.tex        # 附录/补充材料（可选）
```

---

## 子命令详细行为

### audit（体检）

扫描目标目录，检查以下问题并输出报告：

| 检查项 | 违规条件 | 严重度 |
|--------|----------|--------|
| 入口唯一性 | 根目录有多个 `*.tex`（排除 scratch/）| HIGH |
| 图片目录统一 | 存在 figures/、figures_*/、figs/ 等目录 | HIGH |
| 编译产物 | 根目录有 .aux .log .out .toc .fls .fdb_latexmk .xdv .synctex.gz | MEDIUM |
| 脚本散落 | 根目录有 *.py（排除单文件项目）| MEDIUM |
| 手写参考文献 | main*.tex 含 `\begin{thebibliography}` | MEDIUM |
| 测试文件 | 根目录有 test_*.tex | LOW |
| 多版本脚本 | 存在 foo.py 和 foo_v2.py 同名脚本 | LOW |
| 备份文件 | 存在 *.bak、*.volleyball_backup 等非规范备份 | LOW |
| gitignore 缺失 | 无 .gitignore | LOW |
| tmp_ 文件 | 根目录有 tmp_*.txt/py | LOW |

输出格式：
```
=== Paper Scaffold Audit: <路径> ===

[HIGH]   多个 tex 入口：main.tex, main_agl.tex, main_agl_test.tex
[HIGH]   图片目录分散：figures/(16), figures_optimized/(15), figures_replicated/(6) — 应合并到 images/
[MEDIUM] 编译产物在根目录：9 个文件（.aux .log .out ...）
[MEDIUM] Python 脚本散落根目录：62 个，建议归入 scripts/
[MEDIUM] 使用 \begin{thebibliography} 手写参考文献，建议迁移到 refs.bib
[LOW]    22 个 test_*.tex 在根目录，建议移入 scratch/
[LOW]    多版本脚本：fix_font.py / fix_font_v2.py / fix_font_v3.py
[LOW]    非规范备份文件：main.tex.volleyball_backup
[LOW]    缺少 .gitignore

共 9 项问题，其中 HIGH: 2  MEDIUM: 3  LOW: 4
运行 /paper-scaffold fix <路径> 自动修复
```

### init（初始化）

在指定路径创建标准骨架。步骤：

1. 检查目标路径是否已存在，若非空则询问是否继续
2. 创建标准目录树（含 .gitkeep）
3. 根据 `--type` 写入 main.tex 模板（见下方模板内容）
4. 写入空 refs.bib
5. 写入 .gitignore

执行后输出创建的文件列表和下一步提示。

### fix（自动修复）

对现有目录执行以下操作（每步执行前输出将做什么，完成后确认）：

1. **创建缺失目录**：scripts/fix scripts/plot scripts/tmp drafts scratch build archive
2. **移动脚本**：
   - `fix_*.py` → `scripts/fix/`
   - `tmp_*.py` → `scripts/tmp/`
   - `plot_*.py` / `draw_*.py` / `heatmap_*.py` / `optimize_*.py` / `replicate_*.py` / `extract_*.py` → `scripts/plot/`
   - 其余 `.py`（insert, draft, analyze, check, apply, verify, restore）→ `scripts/insert/`（或 `scripts/fix/`）
3. **合并图片目录**：将 figures/ figures_*/ figs/ 中的图片复制到 images/，原目录移入 archive/，更新 main.tex 中对应的路径引用（`sed` 替换）
4. **移动编译产物**：`.aux .log .out .toc .fls .fdb_latexmk .xdv .synctex.gz` → `build/`
5. **移动测试 tex**：`test_*.tex` → `scratch/`
6. **移动草稿文本**：`draft_*.txt` `sec_*.txt` `chapter*.txt` `tmp_*.txt` `page_*.txt` `*_bak` `*.bak` → `drafts/` 或 `archive/`
7. **写入 .gitignore**（若不存在或补全缺失条目）

### biblatex（迁移参考文献）

将 `\begin{thebibliography}` 手写参考文献迁移到 BibTeX。步骤：

1. 从 main.tex 中提取所有 `\bibitem` 条目
2. 按格式解析，转换为 BibTeX 条目写入 `refs.bib`
   - 无法自动解析的条目保留为 `@misc{key, note={原始文本}}` 并标注 `% TODO: verify`
3. 在 main.tex 导言区添加：
   ```latex
   \usepackage[backend=biber,style=gb7714-2015]{biblatex}
   \addbibresource{refs.bib}
   ```
4. 将正文 `\cite{key}` 保持不变（biblatex 兼容）
5. 替换 `\begin{thebibliography}...\end{thebibliography}` 为：
   ```latex
   \printbibliography[title={参考文献}]
   ```
6. 输出迁移报告：条目总数、自动解析成功数、需人工检查数

---

## .gitignore 标准内容

```gitignore
# LaTeX 编译产物
build/
*.aux
*.log
*.out
*.toc
*.fls
*.fdb_latexmk
*.xdv
*.synctex.gz
*.synctex(busy)
*.bbl
*.blg

# Python 缓存
scripts/__pycache__/
**/__pycache__/
*.pyc
*.pyo

# 本地临时目录（不提交）
scratch/
drafts/

# 编辑器
*.swp
.DS_Store
Thumbs.db
```

---

## main.tex 模板

### CIT 毕业设计模板（--type cit）

```latex
% !TeX program = XeLaTeX
% 常州工学院毕业设计说明书
\documentclass[zihao=-4,fontset=windows,openany,oneside]{ctexbook}

\usepackage[paper=a4paper,top=2.5cm,bottom=2.1cm,
  left=2.1cm,right=2.1cm,bindingoffset=0.5cm,
  headheight=15pt,headsep=0.5cm,footskip=0.8cm]{geometry}

\usepackage{fontspec}
\setmainfont{Times New Roman}
\setsansfont{Arial}
\setmonofont{Courier New}

\usepackage{amsmath,amsfonts,amssymb}
\usepackage{graphicx}
\graphicspath{{./images/}}
\usepackage{booktabs,multirow,threeparttable}
\usepackage{caption,subcaption}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{setspace}
\usepackage{hyperref}
\usepackage{xurl}
\hypersetup{colorlinks=true,linkcolor=black,citecolor=black,urlcolor=black}

% biblatex — GB/T 7714-2015
\usepackage[backend=biber,style=gb7714-2015]{biblatex}
\addbibresource{refs.bib}

\setstretch{1.25}
\setlength{\parindent}{2em}

% \input{sections/chapter1}
% \input{sections/chapter2}

\begin{document}

% 封面、摘要、目录 ...

\printbibliography[title={参考文献}]
\end{document}
```

### 国际会议模板（--type icml）

```latex
% !TeX program = pdfLaTeX
% ICML 2025 — replace icml2025 with target venue sty
\documentclass{article}

\usepackage{microtype}
\usepackage{graphicx}
\graphicspath{{./images/}}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage[accepted]{icml2025}
\usepackage{amsmath,amssymb,mathtools}

% biblatex (optional — some venues require natbib)
% \usepackage[backend=biber,style=numeric-comp]{biblatex}
% \addbibresource{refs.bib}

\begin{document}
\twocolumn[
  \icmltitle{Title}
  \icmlauthor{Author}{affil}
  \icmlaffiliation{affil}{Institution}
  \icmlcorrespondingauthor{Author}{email@example.com}
  \icmlkeywords{keyword1, keyword2}
  \vskip 0.3in
]

% \input{sections/intro}
% \input{sections/method}
% \input{sections/experiments}

\bibliography{refs}
\bibliographystyle{icml2025}
\end{document}
```

### 通用学术模板（--type generic）

```latex
% !TeX program = XeLaTeX
\documentclass[12pt,a4paper]{article}

\usepackage[margin=2.5cm]{geometry}
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{Microsoft YaHei}
\setmainfont{Times New Roman}

\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\graphicspath{{./images/}}
\usepackage{booktabs,multirow}
\usepackage{caption}
\usepackage{hyperref}
\usepackage[backend=biber,style=gb7714-2015]{biblatex}
\addbibresource{refs.bib}

\begin{document}

\title{论文标题}
\author{作者}
\date{\today}
\maketitle

\begin{abstract}
摘要内容。
\end{abstract}

% \input{sections/intro}

\printbibliography
\end{document}
```

---

## 执行规则

- **只读操作**（audit）不修改任何文件
- **fix 操作**在执行前打印操作清单，等待用户确认后再执行
- 移动文件前检查目标路径是否已存在同名文件，有冲突则跳过并报告
- 更新 tex 文件中的图片路径时，使用 `sed -i` 替换，替换后用 grep 验证无残留旧路径
- `sections/` 目录的使用是建议而非强制——若正文已在 main.tex 内内联，不强制拆分
- Windows 路径：shell 中统一使用正斜杠；Write/Edit 工具用原始路径

## 与其他 Skill 的协作

- 编译问题 → 交给 `latex-win`
- 生成/编辑 .docx → 交给 `docx`
- 生成 PDF 报告 → 交给 `pdf`
- 搜索参考文献信息 → 交给 `baidu-search` 或 `deep-research`
