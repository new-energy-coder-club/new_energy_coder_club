---
name: pv-storage-bom
description: Generate photovoltaic and energy storage system standard product BOM (Bill of Materials) lists in Excel format. Use when the user needs to create, organize, or optimize PV+storage system configuration lists, standard product packages, pricing tables, or procurement BOMs. Covers residential (5-30kW) and commercial/industrial (100-400kW+) scenarios with Trina Solar 625W modules as the base unit.
---

# PV+Storage Standard Product BOM Generator

Generate standardized BOM Excel files for photovoltaic and energy storage systems.

## Core Workflow

1. **Determine product tiers** based on user scenario (residential ≤20kW / small commercial 100kW / medium 200kW / large 400kW)
2. **Apply productization thinking**: fixed model + fixed quantity = standard SKU, not multiple-choice lists
3. **Use 1-drag-4 string as base unit**: 4×625W = 2.5kW per string, parallel strings to scale
4. **Storage rough-cut 20kWh increments**: 5kWh/cluster (residential HV), 16kWh/cluster (commercial LV), 261kWh cabinet (large commercial)
5. **Generate BOM Excel** with: Cover sheet + BOM sheet(s), product package / PN / description / QTY / unit price / subtotal
6. **Prune to 5 SKUs max**: small commercial first, merge similar tiers

## String Unit Design (Fundamental Building Block)

| Parameter | Value |
|-----------|-------|
| Module | Trina 625W mono PERC |
| String config | 1 MPPT + 4 modules in series = 2.5kW |
| Dimensions | 2382×1134×30mm each |
| Application | Basic building block, parallel N strings for scaling |

Scaling: 2 strings=5kW, 4 strings=10kW, 8 strings=20kW, 12 strings=30kW, 64 strings=160kW (~100kW AC)

## Standard SKU Library (5 SKUs)

| SKU | Scenario | PV Capacity | Storage | Channel Price | Position |
|-----|----------|-------------|---------|---------------|----------|
| B | Small commercial target | 100kW | 48kWh (LV 3 clusters) | ¥134,500 | **#1 Priority** |
| S1 | Residential entry | 5kW | None | ¥5,000 | #2 |
| S3 | Residential large / small commercial transition | 20kW | 10kWh (HV 2 clusters) | ¥46,300 | #3 |
| C | Medium commercial high-end | 200kW | 261kWh (Trina cabinet) | ¥436,000 | #4 |
| D | Large commercial flagship | 400kW | 522kWh (2 Trina cabinets) | ¥854,000 | #5 |

**Pruning rules**: Remove 10kW (merge into 5kW tier), remove 30kW (merge into 20kW tier). Keep only 5 gradients.

## Component Selection Rules

### Module (always Trina 625W)
- PN: 6B001452
- Desc: 625W_12BB_银边框_30mm_竖装_倒斜角_高反_2382*1134mm_Q1
- Batch pricing: ≤50pcs ¥250/pc, ≤200pcs ¥244/pc, ≤500pcs ¥238/pc, >500pcs ¥231/pc

### Inverter
- Residential hybrid: 5kW HN000501 (¥8,000), 10kW HN001001 (¥8,300), 20kW HN002001 (¥10,500)
- Commercial string: GoodWe GW100K-HT (¥14,000), Sungrow SG110CX (¥16,500)
- **Never use BYD or Ginlong (锦浪)**

### Storage
- Residential HV: 5kWh/cluster (100Ah), PN ES000501, ¥6,000/cluster
- Commercial LV: 16kWh/cluster (314Ah), PN ES031401, ¥12,500/cluster
- Large commercial: Trina Potentia 261kWh liquid-cooled cabinet, PN ES261000, ¥214,000
- **Always prefer Trina Potentia for 261kWh cabinets**

## BOM Excel Structure

Two sheets minimum:

1. **Cover sheet**: 5-SKU overview table with SKU code / name / PV capacity / storage capacity / channel price
2. **BOM sheet**: Per-SKU BOM tables with columns: 产品包 / 物料编号 / 产品描述 / 数量 / 单价(元) / 小计(元), followed by 渠道销售价 highlight row

After all SKUs, append an "选配产品" section for optional add-ons (storage expansion, chargers).

## Styling Spec

- Title: 微软雅黑 18-20pt bold, color #1F4E78, centered
- SKU title: 微软雅黑 11pt bold, color #1F4E78, left aligned
- Header row: white font on #1F4E78 fill
- Channel price row: bold red (#C00000) on #FFF2CC highlight
- Borders: thin #CCCCCC on all cells
- Alt rows: #F2F2F2 fill
- Column widths: B=12, C=28, D=50, E=10, F=12, G=12

## Price Calculation Logic

- Module batch price based on total quantity across all strings
- Subtotal = QTY × unit price
- Channel price = sum of all subtotals (rounded to clean number)
- Revenue model: annual savings = annual generation × electricity price, payback = total price / annual savings

## Merge & Prune Guidelines

When user says "too many" or "merge similar":
1. Keep small commercial (100kW) as #1 priority
2. Merge adjacent residential tiers (10kW→5K, 30kW→20kW)
3. Final set: 100kW / 5kW / 20kW / 200kW / 400kW

For detailed component pricing and PN conventions, see `references/pricing-catalog.md`.
