---
name: content-factory
description: "多代理内容生产线。自动化从选题研究到内容创作的全流程。Keywords: 内容创作, 文案, content creation, copywriting."
---

# 内容工厂 — 自动化从选题研究到内容创作全流程

## 概述

自动化从选题研究到内容创作全流程。适用于自媒体运营者批量生产高质量内容、内容团队协同创作、品牌内容矩阵化管理等场景。

**触发关键词**: 内容创作, 文案, content creation, copywriting

## 前置依赖

```bash
pip install requests jinja2 markdown
```

## 核心能力

### 能力1：多平台内容生成——公众号/知乎/小红书/Twitter
多平台内容生成——公众号/知乎/小红书/Twitter

### 能力2：SEO优化写作——自动插入关键词和元描述
SEO优化写作——自动插入关键词和元描述

### 能力3：内容日历管理——规划每周发布排期
内容日历管理——规划每周发布排期


## 命令列表

| 命令 | 说明 | 用法 |
|------|------|------|
| `write` | 生成内容 | `python3 scripts/content_factory_tool.py write [参数]` |
| `calendar` | 管理发布日历 | `python3 scripts/content_factory_tool.py calendar [参数]` |
| `seo` | SEO优化 | `python3 scripts/content_factory_tool.py seo [参数]` |


## 使用流程

### 场景 1

```
生成AI趋势公众号文章
```

**执行：**
```bash
python3 scripts/content_factory_tool.py write --platform wechat --topic 'AI趋势'
```

### 场景 2

```
规划下周内容发布日历
```

**执行：**
```bash
python3 scripts/content_factory_tool.py calendar --plan next-week
```

### 场景 3

```
优化文章SEO
```

**执行：**
```bash
python3 scripts/content_factory_tool.py seo --file article.md
```


## 输出格式

```markdown
# 📊 内容工厂报告

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

### 原有链接
- [内容营销学院策略指南](https://contentmarketinginstitute.com/developing-a-strategy/)
- [内容工厂Agent完整用例](https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/content-factory.md)
- [YouTube内容管道用例](https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/youtube-content-pipeline.md)
### HackerNews
- [HackerNews: AI内容工厂的工作流设计](https://news.ycombinator.com/item?id=46633472)
### Reddit
- [Reddit r/content_marketing: content_marketing社区AI相关讨论](https://www.reddit.com/r/content_marketing/comments/1051686yyz/content_factory_ai/)
### 微信公众号
- [微信公众号: AI内容工厂——批量生产高质量内容](https://mp.weixin.qq.com/s/BANGQTZNYPSUILKTNTAGNE)
### 小红书
- [小红书: 自媒体AI内容工厂——批量生产高质量内容](https://www.xiaohongshu.com/explore/938579234999995451438842)

## 注意事项

- 所有分析基于脚本获取的实际数据，不编造数据
- 数据缺失字段标注"数据不可用"而非猜测
- 建议结合人工判断使用，AI分析仅供参考
- 首次使用请先安装Python依赖：`pip install requests jinja2 markdown`
