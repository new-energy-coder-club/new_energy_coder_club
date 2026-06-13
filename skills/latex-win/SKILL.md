---
name: latex-win
description: Fix and compile LaTeX documents on Windows with TeX Live. Use when the user encounters XeLaTeX compile errors, PDF file lock issues, font warnings, or needs to compile .tex files locally on Windows. Handles common issues: xelatex not in PATH, PDF locked by viewer, CJK font missing, scshape/footskip warnings, resumeSubSubheading overlap.
---

# LaTeX Windows Local Fix Skill

Diagnose and fix LaTeX compilation issues on Windows (TeX Live 2025).

## Environment Facts

- TeX Live 2025 binary path: `C:\texlive\2025\bin\windows\xelatex.exe`
- TeX Live is **NOT** in PATH by default on this machine
- CJK fonts available: `Microsoft YaHei` (`msyh.ttc`), `Noto Sans SC` (`NotoSansSC-VF.ttf`)
- Shell: bash (Git Bash / Claude Code) — use forward slashes or quoted Windows paths
- PDF viewer lock: xdvipdfmx cannot overwrite a PDF open in Adobe Acrobat; SumatraPDF does not lock

## Compile Command

Always use the full path:

```bash
/c/texlive/2025/bin/windows/xelatex.exe -interaction=nonstopmode "path/to/file.tex"
```

If the output PDF is locked, compile to a temp directory first:

```bash
/c/texlive/2025/bin/windows/xelatex.exe -interaction=nonstopmode \
  -output-directory "/c/Users/29711/AppData/Local/Temp" \
  "D:/OneDrive/Desktop/file.tex"
cp "/c/Users/29711/AppData/Local/Temp/file.pdf" "D:/OneDrive/Desktop/file.pdf"
```

## Common Errors & Fixes

### 1. `xelatex.exe` not found / "无法执行命令"

**Cause:** TeX Live bin directory not in system PATH.

**Fix A — permanent (run PowerShell as admin):**
```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path","Machine") + ";C:\texlive\2025\bin\windows",
  "Machine"
)
```
Then restart the editor.

**Fix B — editor config (TeXstudio):**
> Options → Configure TeXstudio → Commands → XeLaTeX
> Set to: `C:/texlive/2025/bin/windows/xelatex.exe -synctex=1 -interaction=nonstopmode %.tex`

**Fix C — VS Code LaTeX Workshop (`settings.json`):**
```json
"latex-workshop.latex.tools": [{
  "name": "xelatex",
  "command": "C:/texlive/2025/bin/windows/xelatex.exe",
  "args": ["-synctex=1", "-interaction=nonstopmode", "%DOC%"]
}]
```

---

### 2. `xdvipdfmx:fatal: Unable to open "file.pdf"` / Broken pipe

**Cause:** The output PDF is open in a PDF viewer (Adobe Acrobat locks the file).

**Fix:** Close the PDF viewer, then recompile.

**Permanent fix:** Switch to **SumatraPDF** — it does not lock PDF files and supports hot-reload.
TeXstudio: Options → Configure → Viewer → External viewer → set SumatraPDF path.

---

### 3. `Font shape 'TU/lmr/bx/sc' undefined` / `scshape` warning

**Cause:** `\scshape` used with a CJK font (Microsoft YaHei has no small-caps variant).

**Fix:** Remove `\scshape` from headings and `\titleformat`:
```latex
% Before
\textbf{\Huge \scshape Name}
\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}...

% After
\textbf{\Huge Name}
\titleformat{\section}{\vspace{-4pt}\raggedright\large\bfseries}...
```

---

### 4. `\footskip is too small (0.0pt)`

**Cause:** `\usepackage[empty]{fullpage}` sets footskip to 0.

**Fix:** Add after the margin adjustments:
```latex
\setlength{\footskip}{4pt}
```

---

### 5. `Font shape 'TU/MicrosoftYaHei/m/it' undefined`

**Cause:** `\textit{}` applied to CJK text — Microsoft YaHei has no italic variant.

**Fix:** Remove `\textit` wrappers from `\resumeSubheading` subtitle rows:
```latex
% Before
\textit{\small#3} & \textit{\small #4} \\
% After
\small#3 & \small #4 \\
```

---

### 6. Text overlap below `\resumeSubSubheading{Stack: ...}{}`

**Cause:** `\resumeSubSubheading` ends with `\vspace{-7pt}`, stacking on top of `\resumeItemListEnd`'s `\vspace{-5pt}` = −12pt total, pulling the next entry up.

**Fix:** Replace Stack lines with a custom `\resumeStack` command:
```latex
% Add to preamble (requires \usepackage{xcolor}):
\newcommand{\resumeStack}[1]{%
  \item\hspace{0.1in}{\footnotesize\color{gray}#1}\vspace{1pt}}

% Usage (inside \resumeSubHeadingListStart, after \resumeItemListEnd):
\resumeStack{Stack: Yocto $\cdot$ Bitbake $\cdot$ QEMU}
```

---

### 7. `Noto Sans CJK SC` not found

**Cause:** Full CJK variant not installed; only `Noto Sans SC` (variable font) is present.

**Fix:** Use `Microsoft YaHei` instead:
```latex
\setCJKmainfont{Microsoft YaHei}[BoldFont=Microsoft YaHei]
```
For Overleaf, use `Noto Sans CJK SC` (pre-installed there).

---

### 8. Section title text overlap (`\textnormal{\small(...)}` in `\section{}`)

**Cause:** Nested font commands inside `\section{}` interact with `\titlerule \vspace{-5pt}`.

**Fix:** Use `\normalfont\small` inline, and reduce the after-rule vspace:
```latex
\section{Key Achievements \normalfont\small(5 of 12+ projects)}
% and in \titleformat:
}{}[\color{black}\titlerule \vspace{-3pt}]  % was -5pt
```

---

## CJK Font Setup (XeLaTeX)

```latex
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{Microsoft YaHei}[BoldFont=Microsoft YaHei]
% Compile with: xelatex (NOT pdflatex)
```

## File Writing Rules

- **Never use bash heredoc for Chinese content** — shell encoding pipeline corrupts UTF-8 CJK characters
- Always write `.tex` files with the Write/Edit tools (guaranteed UTF-8)
- Never use `sed -i` on Windows bash for multi-line replacements — it can zero-out the file; use Edit tool instead

## Workflow for This Project

Current CV files:
- Source: `C:\Users\29711\AppData\Local\Temp\cv_latex_en.tex` (master copy)
- Source: `C:\Users\29711\AppData\Local\Temp\cv_latex_zh.tex`
- Output: `D:\OneDrive\Desktop\CV-DarrrnPig-HongBird2026-LaTeX-EN.tex` (copy for compilation)
- Output: `D:\OneDrive\Desktop\CV-DarrrnPig-HongBird2026-LaTeX-ZH.tex`

Standard compile + copy workflow:
```bash
cp /c/Users/29711/AppData/Local/Temp/cv_latex_en.tex \
   "/d/OneDrive/Desktop/CV-DarrrnPig-HongBird2026-LaTeX-EN.tex"
cd "/d/OneDrive/Desktop"
/c/texlive/2025/bin/windows/xelatex.exe -interaction=nonstopmode \
   "CV-DarrrnPig-HongBird2026-LaTeX-EN.tex" 2>&1 | grep -E "rror|arning|Output|pages" | grep -v rerunfile
```
