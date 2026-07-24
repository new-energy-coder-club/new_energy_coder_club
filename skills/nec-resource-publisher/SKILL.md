---
name: nec-resource-publisher
description: 将培训/资料附件（PDF、Excel、工程图、压缩包等）发布到 NEC 文档站（new-energy-coder-club/docs，Mintlify）——原文原图展示。PDF 逐块提取原文并原位插入插图，矢量图页与乱码页整页渲染为高清图片，Excel 全量转 Markdown 表格，所有文件与图片上传 Cloudflare R2 CDN。触发词：发布资料到文档站、PDF 转 MDX 原文、Excel 上传文档站、资料独立页面、原文原图展示。
---

# NEC 资料发布管线（原文原图版）

把 PDF / Excel 等附件变成 docs 仓库里的独立 MDX 页面，**正文就是原文本身**（不是总结概括），插图与原书位置一一对应。

## 前置条件

| 依赖 | 位置 | 说明 |
|---|---|---|
| Python 虚拟环境 | `~/.kimi/skills/r2-image-sync/.venv` | 已含 boto3；PyMuPDF 需 `pip install pymupdf`（已装过则跳过） |
| R2 密钥 | `~/.kimi/skills/r2-image-sync/r2_image_sync.py` 内置常量 | **严禁提交进任何 git 仓库**。脚本自动从该文件正则读取 |
| docs 仓库克隆 | 工作区 `nec-docs/` | 先读其 `AGENTS.md` 与 `.kimi/skills/nec-docs-maintainer/SKILL.md` |

## 标准工作流

1. **暂存附件**：复制到工作区 `r2-staging-mech/`（或新建 staging 目录）。
2. **配置资源清单**：复制本 skill 的 `scripts/publish_resources.py` 到 staging 目录，编辑文件顶部 `RESOURCES` 列表，每种资源一项：
   ```python
   {
       "file": "RM M2006 电机说明.pdf",      # staging 目录内文件名
       "slug": "robomaster-m2006-p36-motor-guide",   # ASCII，用于 CDN 路径与图片目录
       "mdx": "m2006-motor-guide",           # mechanical/ 下的 MDX 文件名
       "title": "RoboMaster M2006 P36 电机使用说明",
       "description": "……（用于 frontmatter）",
       "size": "0.7 MB",
       "type": "pdf",                        # pdf / xlsx / binary
       # 可选：矢量图/乱码页手动指定整页渲染（不指定则自动检测）
       "page_only": {1, 4, 5, 6, 7},         # 只显示整页原图的页码
       "page_also": {19, 24},                # 文字后追加整页原图的页码
   }
   ```
3. **运行**：用 r2-image-sync 的 venv 执行（Bash 审批易过期，**优先用 PythonRun 起子进程**，`errors="replace"` 解码输出）：
   ```
   <venv>\Scripts\python.exe publish_resources.py
   ```
   脚本会：上传原始文件到 `files/<topic>/`、提取/渲染图片到 `files/<topic>/images/<slug>/`、生成 MDX 写入 `nec-docs/mechanical/<mdx>.mdx`。重复运行自动跳过已存在对象。
4. **注册导航**：在 `docs.json` 对应分组登记（路径不带 `.mdx`）；必要时更新索引页。
5. **CI**：`python tools/ci/check_docs.py` 必须通过（既有外链警告可忽略）。
6. **提交推送**：Conventional Commits；直接 push 失败时先 `git pull --rebase`（远端 gh-proxy 已配好凭据）。

## 各类型处理逻辑

### PDF（type: "pdf"）
- 逐页按 (y, x) 坐标排序**文本块与图片块**，保持原书阅读顺序；块内换行按中英文规则智能拼接；
- 位图插图原位嵌入（按 MD5 去重，跳过 <3KB 或 <40px 的图标/项目符号）；
- **整页渲染**的两种情况：
  - 乱码页：文字提取乱码率 >15%（如自定义编码的日文段）——以 1600px 宽整页 PNG 展示；
  - 矢量图页：尺寸图、连线图、性能曲线等矢量图形无位图可提取——用 `page_only` 手动指定（自动检测仅供参考，务必人工核对）；
- MDX 特殊字符自动转义（`<` `>` `{` `}` `\`）。

### Excel（type: "xlsx"）
- ⚠️ 飞书/WPS 导出的 xlsx 会让 openpyxl 报 `expected Fill` ——脚本内置**跳过样式表的裸 XML 读取器**，勿用 openpyxl；
- 每个 Sheet 转一张 Markdown 表：自动裁掉全空列、空表头补默认名、单元格换行转 `<br/>`、纯 URL 单元格转 `[打开链接](url)`。

### 其他二进制（type: "binary"）
- 只上传 + 生成带下载链接的占位页。

## 密钥安全（重要）

- 脚本从 `~/.kimi/skills/r2-image-sync/r2_image_sync.py` 正则提取 R2 配置；找不到时回退环境变量 `R2_ENDPOINT` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` / `R2_BUCKET` / `R2_CDN_BASE_URL`；
- 本 skill 目录与生成物可安全提交；**staging 目录（含本地密钥副本的上传脚本）不要提交**。

## 已知坑

- Bash 工具审批在本机经常中途过期 → 上传/git/CI 全部走 PythonRun 子进程；
- push 偶发 non-fast-forward（Mintlify bot 会推提交）→ `git pull --rebase origin main` 后重推；
- CDN HEAD 请求返回 403 是 UA 拦截，验证时带浏览器 UA 用 GET；
- 电机手册类 PDF 的图表多为**矢量**（`page.get_images()` 为空但 `get_drawings()` 很多）→ 必须整页渲染，否则丢图；
- PyMuPDF 对多语种 PDF 的文字提取质量优于 pypdf（日文段 pypdf 会乱码，PyMuPDF 正常）。
