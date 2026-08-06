---
name: redline-credit-excel
description: 在项目收资/并购测算 Excel 表右侧追加"红线资信信息"列——对表内主体（项目公司/用能企业）批量查询失信被执行人、被执行人、终本案件、行政处罚、经营异常 5 项红线维度并写入新列（保留原表样式）。触发词：红线资信、红线资信信息列、资信信息列、查红线、失信被执行查询写入、增加资信列、更新查询红线资信。当用户给出 Excel 文件并要求"更新/查询/增加红线资信信息列"时使用。
---

# 红线资信信息列写入

## 口径

红线资信 = 5 个维度（与 `资信情况/` 目录既有扫描口径一致）：

| 模块 | 维度 |
|---|---|
| `BreakFaithExecutorInfoList` | 失信被执行人 |
| `JudicialExecutorInfoList` | 被执行人 |
| `FinalCaseInfoList` | 终本案件 |
| `AdmPenalInfoList` | 行政处罚 |
| `AbnormalInfoList` | 经营异常 |

数据源：`corporate-deep-query` skill 的 `query_corporate.py`（**必须用 `--env prod`**，test 无真实数据）。

## 流程

1. **读表定位**：用 openpyxl 读 Excel，确认主体列（默认表头"项目公司"；若用户要求查业主/用能企业则换对应列）。注意跳过后续含公式（如 `=SUM(...)`）的汇总行。
2. **锁定信用代码**：对去重后的每个主体，调 qcc MCP `get_company_by_query` 拿统一社会信用代码。出现多候选时必须列给用户选定，禁止自动取第一名。
3. **跑脚本写入**：

```bash
python scripts/redline_credit_column.py --file "<Excel路径>" \
    --entity-col 项目公司 \
    --codes '{"公司A":"91xxxxxxxxxxxxxxxx","公司B":"91xxxxxxxxxxxxxxxx"}'
```

脚本自动完成：逐主体查 5 维度 → 表尾追加（或覆盖已有）"红线资信信息"列 → 样式/列宽复制自原最后一列 → 保存原文件。

- 主体列名不同用 `--entity-col` 指定；多工作表用 `--sheet` 指定。
- 未传 `--codes` 时脚本退出码 2 并列出待锁定主体，回到第 2 步补齐后重跑。
- 结果无记录写作"无失信被执行人记录"等；有记录标 `⚠ 维度 N 条`，此时应另用原子工具查明细向用户报告。
4. **交付**：文件就地更新。若用户要求"发送到桌面"，复制到 `D:\OneDrive\Desktop\`（OneDrive 桌面）与 `C:\Users\29711\Desktop\` 各一份。

## 注意

- Excel 会被脚本**就地覆盖**，用户在意原文件时先备份或操作 `.bak` 副本。
- 单元格文本含查询日期，格式：`公司名（代码）\n经查询（YYYY-MM-DD）：无失信被执行人记录、无被执行人记录、无终本案件、无行政处罚、无经营异常`。
- 表头模糊（如同时有"项目公司"和"业主"列）时先问用户查哪一类主体，不要猜。
