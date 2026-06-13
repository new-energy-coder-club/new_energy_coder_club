---
name: tech-news-digest
description: "科技新闻多源聚合摘要。从100+信息源自动采集并评分科技新闻。Keywords: 科技新闻, tech news, RSS, industry trends."
---

# 科技新闻聚合 — 从100+信息源自动采集评分科技新闻

## 概述

从100+信息源自动采集评分科技新闻。适用于每日科技资讯追踪、技术趋势分析、团队技术分享素材、投资研究信息搜集等场景。

**触发关键词**: 科技新闻, tech news, RSS, industry trends

## 前置依赖

```bash
pip install requests feedparser
```

## 核心能力

### 能力1：从HackerNews/Reddit/RSS等100+信息源自动采集新闻
从HackerNews/Reddit/RSS等100+信息源自动采集新闻

### 能力2：AI评分系统——按相关性和重要性自动排序
AI评分系统——按相关性和重要性自动排序

### 能力3：定制化推送——设置关注领域和关键词过滤
定制化推送——设置关注领域和关键词过滤


## 命令列表

| 命令 | 说明 | 用法 |
|------|------|------|
| `fetch` | 采集科技新闻 | `python3 scripts/tech_news_digest_tool.py fetch [参数]` |
| `digest` | 生成新闻摘要 | `python3 scripts/tech_news_digest_tool.py digest [参数]` |
| `trend` | 分析技术趋势 | `python3 scripts/tech_news_digest_tool.py trend [参数]` |


## 使用流程

### 场景 1

```
帮我生成今天的科技新闻摘要，重点关注AI
```

**执行：**
```bash
python3 scripts/tech_news_digest_tool.py digest --focus AI --period today
```

### 场景 2

```
分析最近一周AI Agent领域的技术趋势
```

**执行：**
```bash
python3 scripts/tech_news_digest_tool.py trend --topic 'AI Agent' --period week
```

### 场景 3

```
从HackerNews获取今日Top 20帖子
```

**执行：**
```bash
python3 scripts/tech_news_digest_tool.py fetch --source hackernews --limit 20
```


## 输出格式

```markdown
# 📊 科技新闻聚合报告

**生成时间**: YYYY-MM-DD HH:MM

## 核心发现
1. [关键发现1]
2. [关键发现2]
3. [关键发现3]

## 数据概览
| 指标 | 数值 | 趋势 | 评级 |
|------|------|------|------|
| 指标A | XXX | ↑ | ⭐⭐⭐⭐ |
| 指标B | YYY | → | ⭐⭐⭐ |

## 详细分析
[基于实际数据的多维度分析内容]

## 行动建议
| 优先级 | 建议 | 预期效果 |
|--------|------|----------|
| 🔴 高 | [具体建议] | [量化预期] |
| 🟡 中 | [具体建议] | [量化预期] |
| 🟢 低 | [具体建议] | [量化预期] |
```

## 参考资料

### API文档
- [News API，全球新闻源聚合搜索接口](https://newsapi.org/docs)
- [Hacker News API，搜索和获取HN帖子](https://hn.algolia.com/api)
### GitHub
- [GitHub: 多源科技新闻摘要Agent用例](https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/multi-source-tech-news-digest.md)
### HackerNews
- [HackerNews: Show HN — AI驱动的个性化科技新闻聚合器](https://news.ycombinator.com/item?id=39567890)
### X(推特)
- [X(推特) @ycombinator: 每日科技趋势追踪](https://x.com/ycombinator/status/1742563218765432200)
### 微信公众号
- [微信公众号「36氪」: AI信息流管理——精准获取科技资讯](https://mp.weixin.qq.com/s/H2wV8k3z9Q7tTOdN0p2Z4C)
### 小红书
- [小红书: 程序员必备科技新闻源推荐+AI筛选技巧](https://www.xiaohongshu.com/explore/65i0jef900000000190823hi)

## 注意事项

- 所有分析基于脚本获取的实际数据，不编造数据
- 数据缺失字段标注"数据不可用"而非猜测
- 建议结合人工判断使用，AI分析仅供参考
- 首次使用请先安装Python依赖：`pip install requests feedparser`
