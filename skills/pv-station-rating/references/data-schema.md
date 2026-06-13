# 项目数据 JSON Schema

`scripts/score.py --data project.json` 接收的数据格式。所有字段大小写不敏感。

## 完整字段（推荐传入）

```json
{
  "name": "示例项目：汽车零部件厂",
  "grades": {
    "d1_enterprise": "A",
    "d2_region": "A",
    "d3_self_use": "A",
    "d4_materials": "A",
    "d5a_finance_health": "A",
    "d5b_pv_share": "A",
    "d5c_revenue_cover": "A",
    "d5d_profit_cover": "A",
    "d6_industry": "B"
  },
  "adjustments": {
    "long_term_20mw": false,
    "long_term_50mw": false,
    "strategic": false,
    "storage": true,
    "missing_materials": 0,
    "finance_abnormal": false,
    "red_zone": false
  },
  "veto": {
    "enterprise_d_blacklist": false,
    "finance_d_no_guarantee": false,
    "materials_d_filing_missing": false,
    "industry_d_forbidden": false
  }
}
```

## 字段说明

### grades（必填，6 维度 + 财务 4 子项）

- `d1_enterprise`: 维度 1 企业性质/规模等级 A/B/C/D
- `d2_region`: 维度 2 省份区域
- `d3_self_use`: 维度 3 自发自用比例
- `d4_materials`: 维度 4 材料齐全性
- `d5a_finance_health`: 财务子项 5a 整体财务健康度
- `d5b_pv_share`: 财务子项 5b 光伏电费/总电费
- `d5c_revenue_cover`: 财务子项 5c 营收/光伏电费
- `d5d_profit_cover`: 财务子项 5d 净利润/光伏电费
- `d6_industry`: 维度 6 行业稳定性

简版若用户**只**给 `d5_finance` 一个总评（A/B/C/D），脚本会把 5a/5b/5c/5d 都填成同一等级（粗略，可用）。

### adjustments（可选，加减分）

- `long_term_20mw`: 年度合作 ≥20MW（与 50MW 互斥，取后者）
- `long_term_50mw`: 年度合作 ≥50MW
- `strategic`: 战略协同（央国企 + 3 年以上协议 / 批量合作）
- `storage`: 配套储能 ≥光伏装机 10%
- `missing_materials`: 重大材料缺失项数（int，最多 5，超过封顶）
- `finance_abnormal`: 近 1 年亏损或经营性现金流为负
- `red_zone`: 区县电网承载力红色预警

### veto（可选，一票否决，任一为 true 直接定 D）

- `enterprise_d_blacklist`: 失信 / 重大税务违规 / 经营异常
- `finance_d_no_guarantee`: 财务 D 且无强担保
- `materials_d_filing_missing`: 备案或接入批复缺失
- `industry_d_forbidden`: 行业 D（房地产 / P2P / 教培）

## 最小字段（懒人版）

如果调用方只关心简版结论，可以**不传** d5a/b/c/d，把 d5 写成单一等级：

```json
{
  "name": "示例 5：建材经销商",
  "grades": {
    "d1_enterprise": "C",
    "d2_region": "C",
    "d3_self_use": "D",
    "d4_materials": "C",
    "d5_finance": "C",
    "d6_industry": "D"
  },
  "adjustments": {"red_zone": true}
}
```

脚本会自动把 d5_finance 展开成四个子项再做复杂版评分（精度有损，会在报告中提示）。
