---
name: feishu-to-nec-mdx
version: 2.0.0
description: "把飞书文档/Wiki 导入 NEC Mintlify 文档站（docs.newenergycoder.club）：lark-cli 抓取正文与图片、生成合规 .mdx、注册 docs.json 导航、跑 CI 并推送。内含中国大陆受限网络下的 GitHub 克隆/推送方案（gh-proxy 镜像 + SSH 通道）。触发词：飞书转 mdx、飞书转 NEC 文档、导入飞书到文档站、wiki 导入 docs、feishu to mdx。"
metadata:
  requires:
    bins: ["lark-cli", "git", "python"]
---

# 飞书 → NEC 文档站（MDX）

把飞书文档或 Wiki 页面转化为 NEC Mintlify 文档站的 `.mdx` 页面并发布。2026-07 实测全流程（lark-cli 1.0.72 / Windows Git Bash）。

## 前置条件

- 已安装并登录 `lark-cli`（`lark-cli auth status` 显示 bot/user 均 ready）
- **Windows Git Bash 坑**：`node` 常不在 PATH，`lark-cli` 会报 `exec: node: not found`。先执行：
  ```bash
  export PATH="/c/Program Files/nodejs:/c/Users/$USER/AppData/Roaming/npm:$PATH"
  ```
- 文档站仓库：`https://github.com/new-energy-coder-club/docs`（克隆方案见文末「受限网络」）
- 导入前确认用户已授权公开该飞书内容

## 全流程

### 1. 解析 wiki 节点

```bash
lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}'
```

从 URL 取 token（`/wiki/<token>`），返回 `obj_token`、`obj_type`（docx/sheet/…）、`title`、`has_child`、`space_id`。sheet/bitable/slides/mindnote 不可转 mdx。

- 单页：直接用 `obj_token` 抓内容
- 子树：`lark-cli api GET /open-apis/wiki/v2/spaces/<space_id>/nodes --params '{"parent_node_token":"<node_token>","page_size":50}'` 逐层遍历

### 2. 抓取正文（新版 v2 命令）

```bash
lark-cli docs +fetch --doc <obj_token> --doc-format markdown --scope full --format json > doc.json
```

<Warning>
旧版 `--limit/--offset` 分页已废弃（报 `docs +fetch is v2-only`）。部分读取用 `--scope outline/section/range/keyword`。命令 schema 以 `lark-cli docs +fetch --help` 为准，不要照抄旧脚本。
</Warning>

正文在返回 JSON 的 `data.document.content` 字段。

### 3. 下载图片

markdown 里的图片是带时效 authcode 的 CDN 链接，`internal-api-drive-stream.feishu.cn` 在受限网络下 curl 直连经常 000——**不要 curl 直拉，走 lark-cli API**：

```bash
# 1) 重新以 XML 抓取，拿图片 token（<img src="..."> 的 src 属性）
lark-cli docs +fetch --doc <obj_token> --doc-format xml --detail with-ids --scope full --format json > doc_xml.json

# 2) 逐个下载（--output 必须是相对路径，扩展名自动识别 png/webp）
lark-cli docs +media-download --token <img_token> --output imgs/img_01 --overwrite
```

下载后复制到文档站 `images/<topic>/`，建议语义化命名。

### 4. 生成 .mdx

- 文件放主题目录（如 `mechanical/`、`ai-tools/`），命名为标题 slug
- frontmatter 必填非空 `title` 与 `description`：

  ```mdx
  ---
  title: "页面标题"
  description: "页面描述"
  ---
  ```

- 飞书 `<callout>` → Mintlify `<Info>` / `<Note>` / `<Warning>`；步骤用 `<Steps>/<Step>`，FAQ 用 `<AccordionGroup>/<Accordion>`
- 图片引用 `/images/<topic>/<name>`；删除飞书私有标签（`<view>` 等）
- 内部链接以 `/` 开头且可解析，不含 localhost 与非 ASCII 路径

### 5. 注册导航

在 `docs.json` 的 `navigation` 对应 tab/group 中加入页面路径（不带扩展名）。空菜单不上线：目标页面必须已存在且有实质内容。

### 6. CI 检查

```bash
python tools/ci/check_docs.py
```

检查 docs.json 合法性、导航页面存在性、frontmatter、死链、归档目录回潮等（错误级）；另有 497+ 外链探测（仅警告级）。**受限网络下外链探测会挂起**，本地验证可跳过：

```bash
python - <<'EOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("check_docs", "tools/ci/check_docs.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.check_external_url = lambda url: None
sys.exit(m.main())
EOF
```

### 7. 提交与推送

Conventional Commits：`docs(<topic>): import from Feishu <source-title>`。推送方案见下。

## 受限网络下的 GitHub 方案（中国大陆实测）

| 操作 | 方案 | 说明 |
|---|---|---|
| 克隆/拉取 | `https://gh-proxy.com/https://github.com/<org>/<repo>.git` | 仅拉取；中途断流（early EOF）则重试，或 `--depth 1`；再不行下载 `archive/refs/heads/<branch>.zip` 兜底 |
| 推送 | **SSH 通道** | HTTPS 443 被 RST、镜像不支持推送，但 `ssh.github.com:22` 通常可达 |
| 图片/媒体 | lark-cli API | `internal-api-drive-stream.feishu.cn` 直连不通，`open.feishu.cn` 走 lark-cli 正常 |

SSH 推送开通步骤：

```bash
# 1. 探测通道（通则有戏）
ssh -T git@github.com   # 期望: Hi <user>! ... / Permission denied (publickey) 也算网络通

# 2. 无密钥则生成，把 .pub 内容加到 GitHub Settings → SSH keys
ssh-keygen -t ed25519 -C "<标记>" -f ~/.ssh/id_ed25519 -N ""

# 3. remote 改为 SSH 地址后推送
git remote set-url origin git@github.com:<org>/<repo>.git
git push origin main
```

网络探测速查：`curl -sI --max-time 8 <url> -o /dev/null -w "%{http_code}"`（000 = 被阻断）；`timeout 2 bash -c "echo > /dev/tcp/<host>/<port>"` 探端口；`GIT_TERMINAL_PROMPT=0` 防止凭据弹窗挂起脚本。

## 质量标准

- 每个 `.mdx` 都有非空 `title` 和 `description`
- 无 `<image token="...">`、`<file token="...">`、`<whiteboard token="...">` 残留
- 图片引用路径以 `/images/<topic>/` 开头（或仓库约定的 CDN 地址）
- `docs.json` 新增页面均已注册，`check_docs.py` 通过
- 大批量图片可考虑转 CDN（仓库先例：`cdn.newenergycoder.club`，见 commit `caa47ee`）

## 实战案例（2026-07-18）

- 抓取 `https://tcnyw794ws3e.feishu.cn/wiki/LVXow8r6MiKV5KkbJgZcMZUrnPg`（LumenPnP 介绍页，docx + 10 图）→ `mechanical/lumenpnp-introduction.mdx`
- 整理 [飞书 CLI 官网](https://www.feishu.cn/feishu-cli) 内容并经本机 lark-cli 验证 → `ai-tools/feishu-cli.mdx`
- 两页注册 docs.json，CI 通过，commit `93b0607` 经 SSH 推送，Mintlify 自动部署
