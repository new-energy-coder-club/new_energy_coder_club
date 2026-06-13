# 自动填写流程（端到端）

> 目标：用户只需提供「项目原始信息」（或一个 xlsx），就能自动得到评级 + Markdown 报告 + 写回模板的 xlsx。

```
┌──────────────────┐
│ 输入：项目原始信息 │
│  - 自然语言        │
│  - JSON 文件       │
│  - xlsx 模板某行   │
└────────┬─────────┘
         │ Step 1：信息抽取与等级映射
         ▼
┌──────────────────┐    references/rating-rules.md
│ project.json      │◄───（六维度 + 财务 4 子项的 A/B/C/D 划分）
│ {grades, adj,     │
│  veto}            │    references/data-schema.md
└────────┬─────────┘
         │ Step 2：评分
         ▼
┌──────────────────┐
│ scripts/score.py  │  ──► Markdown 报告（report.md）
│  --data ...       │  ──► 完整 JSON 结果（report.json，含 step1/step2/irr）
└────────┬─────────┘
         │ Step 3：写回 xlsx（可选）
         ▼
┌──────────────────────────┐
│ scripts/fill_template.py │  ──► <原>_filled.xlsx
│  --template ... --data ...│      （简版/复杂版示例区各追加一行）
└──────────────────────────┘
```

## Step 1 · 信息抽取与等级映射

### 1.1 必须拿到的字段（任意一种来源即可）

| 字段 | 自然语言示例 | 映射逻辑 |
| --- | --- | --- |
| `d1_enterprise` | "央企子公司，营收 30 亿" | 央/国企 + 大型 → A |
| `d2_region` | "项目在江苏南通" | 江苏 → A |
| `d3_self_use` | "年用电量 1200 万 kWh / 年发电 600 万 kWh，自用比 70%" | 70% + 依赖度=优 → A |
| `d4_materials` | "备案+接入齐全，缺消防" | 缺 1 项可补 → B |
| `d5a-d5d` | "营收 30 亿，净利率 4%，光伏年电费 200 万" | 5a B；5b 看占比；5c=30亿/200万=1500 倍 → A；5d 看净利/电费 |
| `d6_industry` | "汽车零部件" | B 级（成熟制造） |

### 1.2 加减分项识别（在原始信息里扫一遍）

- "签了 30MW / 50MW 框架协议" → `long_term_20mw` / `long_term_50mw`
- "央企集采 / 3 年战略协议 / 批量合作" → `strategic`
- "配 600 kW 储能（光伏 5MW）" → 储能/光伏 = 12% ≥ 10% → `storage = true`
- "未提供征信" → `missing_materials += 1`
- "去年亏损 / 经营性现金流为负" → `finance_abnormal = true`
- "项目所在区县电网红色预警" → `red_zone = true`

### 1.3 一票否决检测（命中即终止）

| 触发词 | 设置 |
| --- | --- |
| 失信被执行 / 重大税务违规 / 经营异常 | `enterprise_d_blacklist=true` |
| 财务 D 且无母担保 | `finance_d_no_guarantee=true` |
| 备案缺失 / 未批先建 | `materials_d_filing_missing=true` |
| 房地产 / P2P / 教培 | `industry_d_forbidden=true` |

### 1.4 落库为 project.json

```json
{
  "name": "南通某汽车零部件 5MW 屋顶项目",
  "grades": {
    "d1_enterprise":"A","d2_region":"A","d3_self_use":"A","d4_materials":"B",
    "d5a_finance_health":"B","d5b_pv_share":"A","d5c_revenue_cover":"A","d5d_profit_cover":"A",
    "d6_industry":"B"
  },
  "adjustments":{"long_term_20mw":true,"storage":true},
  "veto":{}
}
```

> 如果有维度没法判定，**一次性**问用户补齐再继续，不要逐项追问。

## Step 2 · 评分（必跑）

```powershell
python C:\Users\29711\.claude\skills\pv-station-rating\scripts\score.py `
    --data project.json `
    --report-md report.md `
    --report-json report.json
```

输出包含：

- 简版三结论（木桶 / 多数 / 是否触发否决）
- 复杂版基础分、加减分明细、最终总分、等级
- 基准 IRR + 调整 + 最终 IRR
- 关键风险点 + 改进建议

如果只想拿数据不想看报告：

```python
from score import score_project
r = score_project(json.load(open("project.json", encoding="utf-8")))
print(r["final_grade"], r["irr"]["final_low"], r["irr"]["final_high"])
```

## Step 3 · 写回 xlsx 模板（可选）

```powershell
python C:\Users\29711\.claude\skills\pv-station-rating\scripts\fill_template.py `
    "D:\OneDrive\Desktop\副本工商业光伏电站分层分级_两步走.xlsx" `
    --data project.json `
    --out "D:\OneDrive\Desktop\已填_副本工商业光伏电站分层分级_两步走.xlsx"
```

行为：

- **默认副本写入**，原文件保持不动；输出 `<原文件名>_filled.xlsx`。
- 在「第一步 简版模式」示例区下方追加一行：项目名 + 6 维度等级 + 综合评级（木桶/多数/否决） + 基准 IRR + 加减项 + 最终 IRR。
- 在「第二步 复杂版模式」示例区下方追加一行：项目名 + 9 列等级/分数 + 基础总分 + 加减分 + 最终总分 + 等级 + 基准 IRR。
- 新增行套用浅黄底 + 蓝字，便于和原示例区分。

### 批量评分多个项目

```powershell
python ...\fill_template.py template.xlsx `
    --data proj1.json --data proj2.json --data proj3.json `
    --out filled.xlsx
```

每个项目各占简版 1 行 + 复杂版 1 行，按传入顺序追加。

### 直接覆盖原文件（不推荐）

```powershell
python ...\fill_template.py template.xlsx --data project.json --in-place
```

会先生成 `<原>.bak.xlsx` 备份再覆盖。

## 完整一键脚本（PowerShell 示例）

```powershell
$skill = "C:\Users\29711\.claude\skills\pv-station-rating\scripts"
$tpl = "D:\OneDrive\Desktop\副本工商业光伏电站分层分级_两步走.xlsx"
$data = "D:\OneDrive\Desktop\project.json"
$report = "D:\OneDrive\Desktop\report.md"
$filled = "D:\OneDrive\Desktop\已填_两步走.xlsx"

# Step 2 评分 + 出报告
python "$skill\score.py" --data $data --report-md $report

# Step 3 写回模板
python "$skill\fill_template.py" $tpl --data $data --out $filled

Start-Process $report
Start-Process $filled
```

## Claude 触发示例

让 Claude 直接帮你跑全流程：

> 「评一下南通某汽车零部件 5MW 项目：央企子公司年营收 30 亿净利 4%，配 600kW 储能，已签 25MW 框架，备案接入齐全缺消防。结果填进 `D:\...\两步走.xlsx`」

Claude 会：

1. 按 §1 把自然语言映射成 `project.json`。
2. 跑 `score.py` 得到报告。
3. 跑 `fill_template.py` 把行追加到 xlsx 副本。
4. 输出 Markdown 报告 + 落地 xlsx 路径。

## 故障处理

| 问题 | 解决方法 |
| --- | --- |
| `非法等级 'a级'` | grade 字段必须是单字母 A/B/C/D（大小写均可） |
| `缺少财务子项 d5a_finance_health` | 简版只给一个 `d5_finance` 即可，脚本自动展开 |
| `找不到含「简版项目评估示例」` | xlsx 不是原模板格式；改用空模板或跳过 fill_template |
| 中文乱码 | 加 `$env:PYTHONIOENCODING="utf-8"` 后再跑 |
| openpyxl 未装 | `pip install openpyxl` |
