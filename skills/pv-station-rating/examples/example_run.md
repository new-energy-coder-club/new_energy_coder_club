# 5 个原表示例的运行结果对照

> 用 `python scripts/score.py --selftest` 即可重现。

| 示例 | 公式精确分 | 公式等级 | Excel 手填分 | Excel 等级 | 说明 |
| --- | --- | --- | --- | --- | --- |
| 1 汽车零部件厂 | 9.95 | A | 10.0 | A | Excel 显示 10.0 应为四舍五入 |
| 2 食品加工厂 | 7.5 | B | 7.5 | B | 完全一致 |
| 3 小型纺织厂 | 5.475 | C | 5.35 | C | Excel 5.75 漏算 0.125；最终等级一致 |
| 4 物流公司 | 8.1 | A | 7.875 | B | **公式 8.1 应入 A 级，Excel 漏算导致定为 B** |
| 5 建材经销商 | 4.0 | C | 4.075 | C | Excel 4.375 多算 0.075；最终等级一致 |

## 处理原则

- **以公式实现为准**：score.py 严格按权重 + 加减分文档计算。
- **简版评级（木桶 / 多数）不受影响**：5 个示例的简版等级与 Excel 完全一致。
- **示例 4 是有意义的差异**：公式 8.1 → A 级，Excel 手填 7.875 → B 级。建议据公式重新审定。

## 示例 1 简版结论复核

简版 R40 显示 "B 级（木桶）"，但 6 个维度是 A,A,A,A,A,B → 木桶最低=B ✓。
脚本输出与 Excel 一致：木桶=B。

## 示例 4 简版结论复核

R43 显示 "B 级（多数）"。6 维度 B,A,C,A,B,B → 4 个 B → 多数=B ✓。
脚本输出：木桶=C，多数=B。Excel 用了多数原则，脚本默认显示木桶；调用方可对照 step1_simple 字段查看两种结论。

## 跑单个示例

```powershell
python C:\Users\29711\.claude\skills\pv-station-rating\scripts\score.py --json '{"name":"示例3：小型纺织厂","grades":{"d1_enterprise":"C","d2_region":"B","d3_self_use":"C","d4_materials":"C","d5a_finance_health":"C","d5b_pv_share":"B","d5c_revenue_cover":"C","d5d_profit_cover":"C","d6_industry":"B"},"adjustments":{"missing_materials":2,"finance_abnormal":true}}'
```

## 从原 xlsx 一键拉所有示例

```powershell
python C:\Users\29711\.claude\skills\pv-station-rating\scripts\parse_template.py "D:\OneDrive\Desktop\副本工商业光伏电站分层分级_两步走.xlsx" --out projects.json
```
