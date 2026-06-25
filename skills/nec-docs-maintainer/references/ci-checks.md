# CI 健康检查说明

## 运行方式

```bash
python tools/ci/check_docs.py
```

## 检查项

| 检查项 | 说明 |
|---|---|
| JSON 合法性 | `docs.json` 必须可解析 |
| 推荐字段 | `metadata`、`search`、`seo`、`styles` 等 |
| 导航页面存在性 | 所有注册页面必须有对应 `.mdx`/`.md` 文件 |
| frontmatter | 所有 `.mdx` 必须含非空 `title` 与 `description` |
| 内部链接 | Markdown / HTML 链接必须可解析 |
| 路径规范 | 无 `localhost` 链接、无非 ASCII 路径 |
| 外部链接 | 抽样 HEAD/GET 检查，白名单域名静默通过 |
| 禁止目录 | 不允许 `legacy/`、`api-reference/`、`essentials/` |

## 常用白名单域名

```python
EXTERNAL_LINK_ALLOWLIST = {
    "gitee.com", "github.com", "feishu.cn", "qm.qq.com",
    "www.cnrobocon.net", "docs.m2stud.io", "pan.baidu.com", "docs.qq.com",
}
```

## 允许的孤儿文件

```python
ALLOWED_ORPHANS = {"AGENTS.md", "snippets/snippet-intro.mdx", "wiki/README.md"}
```

## 处理警告

- 证书错误（SSL）或 403：若链接可正常浏览器访问，加入白名单
- 真实 404：修复或删除链接
- 未注册页面：决定加入导航或删除
