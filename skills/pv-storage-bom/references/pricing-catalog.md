# PV+Storage Component Pricing Catalog

## Module — Trina 625W (6B001452)

| Qty Range | Unit Price (¥) | Notes |
|-----------|---------------|-------|
| ≤50 pcs | 250 | Residential small |
| 51-200 pcs | 244 | Residential large |
| 201-500 pcs | 238 | Medium commercial |
| >500 pcs | 231 | Large commercial |

Desc template: `625W_12BB_银边框_30mm_竖装_倒斜角_高反_2382*1134mm_Q1`

## Inverters

### Residential Hybrid (混逆一体机)

| Model | PN | Power | Price (¥) | Notes |
|-------|-----|-------|-----------|-------|
| HN000501 | 5kW + 10kWh EMS | 8,000 | S1 5kW tier |
| HN001001 | 10kW + 10kWh EMS | 8,300 | S2 10kW tier (merged) |
| HN002001 | 20kW + 40kWh EMS | 10,500 | S3 20kW tier |
| HN003001 | 30kW + 60kWh EMS | 10,500 | S4 30kW tier (merged) |

### Commercial String Inverters

| Brand | Model | Power | Price (¥) | MPPT | PN |
|-------|-------|-------|-----------|------|-----|
| GoodWe | GW100K-HT | 100kW | 14,000 | 3 | NB010001 |
| Sungrow | SG110CX | 110kW | 16,500 | 6 | NB011001 |

**Never use**: BYD inverters, Ginlong (锦浪) inverters

## Storage Systems

### Residential HV Cluster (100Ah, 48V)

| Item | PN | Spec | Unit Price (¥) |
|------|-----|------|----------------|
| HV battery cluster | ES000501 | 100Ah, 5kWh/cluster, 16S1P, 48V | 6,000 |

Scaling: 2 clusters=10kWh, 4=20kWh, 8=40kWh, 12=60kWh

### Commercial LV Cluster (314Ah, 48V)

| Item | PN | Spec | Unit Price (¥) |
|------|-----|------|----------------|
| LV battery cluster | ES031401 | 314Ah, 16kWh/cluster, 1P16S, 48V | 12,500 |

Scaling: 3 clusters=48kWh (B tier), other counts as needed

### Large Commercial Liquid-Cooled Cabinet

| Item | PN | Spec | Unit Price (¥) |
|------|-----|------|----------------|
| Trina Potentia蓝海 | ES261000 | 261kWh liquid-cooled all-in-one | 214,000 |

Always prefer Trina Potentia for 261kWh. Unit price: ¥0.82/Wh.

## Balance of System (BOS)

### Residential

| Item | PN | Description | Price (¥) |
|------|-----|-------------|-----------|
| Mounting kit | QB001251 | Pre-galvanized Al-Mg, 1-drag-4, 625W | 500 per set |
| Electrical kit | RFBZH1647 | Anti-backflow + metering + comm + breaker | 1,500-4,000 scale |
| DC cable kit | XL000501 | 4mm² PV cable, flame retardant, 50-300m | 2,500-19,400 |

### Commercial

| Item | PN | Description | Price (¥) |
|------|-----|-------------|-----------|
| Mounting system | QB002001 | Hot-dip galvanized, 625W, with clamps | 20,000-80,000 scale |
| DC combiner | RFHL0001 | 16-in-1-out, surge protection, 1000V | 5,000 each |
| AC distribution | RFPD0001 | Grid-tie cabinet, metering, anti-islanding | 8,000-15,000 scale |
| Cable kit | XL010001 | DC 4mm² + AC 95-120mm² + tray + ground | 15,000-90,000 scale |

### Optional Accessories

| Item | PN | Description | Price (¥) |
|------|-----|-------------|-----------|
| Storage expansion | ES000101 | HV 5kWh cluster, plug-and-play | 6,000 |
| 261kWh expansion | ES261000 | Trina Potentia cabinet, add-on | 214,000 |
| DC charger | CD120001 | 120kW dual-gun, CCS2/GBT, 4G | 35,000 |

## Channel Price Summary (5-SKU Final)

| SKU | PV | Storage | Total BOM | Channel Price |
|-----|-----|---------|-----------|---------------|
| S1 | 5kW | None | ¥5,000 | ¥5,000 |
| S3 | 20kW | 10kWh | ¥46,300 | ¥46,300 |
| B | 100kW | 48kWh | ¥134,500 | ¥134,500 |
| C | 200kW | 261kWh | ¥436,000 | ¥436,000 |
| D | 400kW | 522kWh | ¥854,000 | ¥854,000 |
