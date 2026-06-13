---
name: weather-advisor
description: "天气顾问。智能天气顾问。实时天气查询、未来7天预报、穿衣建议与出行活动推荐 Keywords: 天气查询, weather, 穿衣建议, 出行提醒."
---

## 概述

智能天气顾问。实时天气查询、未来7天预报、穿衣建议与出行活动推荐 适用于查看实时天气信息等场景。

## 适用范围

**适用场景**：
- 查看实时天气信息
- 获取穿衣建议
- 了解极端天气预警

**不适用场景**：
- 需要实时硬件控制或低延迟响应的场景
- 涉及敏感个人隐私数据的未授权处理

**触发关键词**: 天气查询, weather, 穿衣建议, 出行提醒

## 前置条件

```bash
pip install requests
```

> ⚠️ 首次使用前请确认依赖已安装，否则脚本将无法运行。

## 核心能力

### 能力1：实时天气——温度/湿度/风力/空气质量
实时天气——温度/湿度/风力/空气质量

### 能力2：穿衣建议——基于天气的着装推荐
穿衣建议——基于天气的着装推荐

### 能力3：出行提醒——极端天气预警与活动建议
出行提醒——极端天气预警与活动建议


## 命令列表

| 命令 | 说明 | 用法 |
|------|------|------|
| `now` | 查看天气 | `python3 scripts/weather_advisor_tool.py now [参数]` |
| `outfit` | 穿衣建议 | `python3 scripts/weather_advisor_tool.py outfit [参数]` |
| `alert` | 天气预警 | `python3 scripts/weather_advisor_tool.py alert [参数]` |


## 处理步骤

### Step 1：查看天气

**目标**：查看当前天气

**为什么这一步重要**：这是整个工作流的数据采集/初始化阶段，确保后续步骤基于准确的输入。

**执行**：
```bash
python3 scripts/weather_advisor_tool.py now --city Beijing
```

**检查点**：确认输出包含预期数据，无报错信息。

### Step 2：穿衣建议

**目标**：获取穿衣建议

**为什么这一步重要**：核心处理阶段，将原始数据转化为有价值的输出。

**执行**：
```bash
python3 scripts/weather_advisor_tool.py outfit --city Beijing --activity outdoor
```

**检查点**：确认生成结果格式正确，内容完整。

### Step 3：天气预警

**目标**：查看天气预警

**为什么这一步重要**：最终输出阶段，将处理结果以可用的形式呈现。

**执行**：
```bash
python3 scripts/weather_advisor_tool.py alert --city Beijing --days 3
```

**检查点**：确认最终输出符合预期格式和质量标准。

## 验证清单

- [ ] 依赖已安装：`pip install requests`
- [ ] Step 1 执行无报错，输出数据完整
- [ ] Step 2 处理结果符合预期格式
- [ ] Step 3 最终输出质量达标
- [ ] 无敏感信息泄露（API Key、密码等）

## 输出格式

```markdown
# 📊 天气顾问报告

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
```

## 参考资料

### 原有链接
- [OpenWeatherMap](https://openweathermap.org/)

### GitHub
- [weather-api](https://github.com/topics/weather-api)

### 小红书
- [天气穿搭指南](https://www.xiaohongshu.com/explore/weather-outfit)

## 注意事项

- 所有分析基于脚本获取的实际数据，**不编造数据**
- 数据缺失字段标注"数据不可用"而非猜测
- 建议结合人工判断使用，AI分析仅供参考
- 首次使用请先安装依赖：`pip install requests`
- 如遇到API限流，请适当增加请求间隔
