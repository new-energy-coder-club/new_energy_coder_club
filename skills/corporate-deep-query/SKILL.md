---
name: corporate-deep-query
description: >
  通过 TrinaPower 企业深度信息接口查询企业工商、股东、高管、投资、司法风险、年报等全景数据。
  支持测试环境和生产环境切换。
  使用场景：
  (1) 查询企业深度信息 / 企业画像 / 企业全景数据
  (2) 查询企业股东信息、高管任职、工商变更记录
  (3) 查询企业对外投资、法人对外投资、法人任职信息
  (4) 查询企业司法风险（失信、被执行、行政处罚、经营异常）
  (5) 查询企业年报信息（社保、实缴出资、认缴出资、对外投资）
  (6) 触发词：查企业、企业查询、企业深度查询、getCorporateDeepInfo、trinapower 企业查询、统一社会信用代码查询
---

# Corporate Deep Query

## 快速使用

使用本地脚本 `scripts/query_corporate.py` 发起查询。

### 基础查询（测试环境）

```bash
python scripts/query_corporate.py --code 91320411MA1MXKRA7R
```

### 生产环境查询

```bash
python scripts/query_corporate.py --code 91320411MA1MXKRA7R --env prod
```

### 指定输出模块

```bash
# 仅输出股东信息
python scripts/query_corporate.py --code 91320411MA1MXKRA7R --env prod --module OrgShareInfoList

# 仅输出法人任职信息
python scripts/query_corporate.py --code 91320411MA1MXKRA7R --env prod --module LrServiceInfoList

# 仅输出工商变更记录
python scripts/query_corporate.py --code 91320411MA1MXKRA7R --env prod --module AlterationInfoList
```

### 仅输出统计概览

```bash
python scripts/query_corporate.py --code 91320411MA1MXKRA7R --env prod --summary
```

### 保存原始响应

```bash
python scripts/query_corporate.py --code 91320411MA1MXKRA7R --env prod --output resp.json
```

## 支持的环境

| 环境 | 标识 | URL |
|------|------|-----|
| 测试 | `test` | `https://apigw-test.trinapower.com/...` |
| 生产 | `prod` | `https://apigw.trinablue.com/...` |

**默认使用测试环境**。生产环境需确认调用权限。

## 支持的业务模块

脚本内置以下模块标签映射，通过 `--module` 指定：

- `OrgInfo` — 企业照面信息（企业名称、行业、法人、注册资本、地址等）
- `OrgShareInfoList` — 股东信息
- `SharePersonalInfoList` — 高管信息
- `AlterationInfoList` — 工商变更记录
- `LrInvestmentInfoList` — 法人对外投资
- `LrServiceInfoList` — 法人任职信息
- `OrgInvestmentInfoList` — 企业对外投资
- `PledgedEquitiesInfoList` — 股权出质
- `BreakFaithExecutorInfoList` — 失信被执行人
- `JudicialExecutorInfoList` — 被执行人
- `AdmPenalInfoList` — 行政处罚
- `AbnormalInfoList` — 经营异常
- `AnnRepBasInfoList` / `AnnRepInsInfoList` / `AnnRepInvInfoList` / `AnnRepPaidInInfoList` / `AnnRepSubInfoList` / `AnnRepModInfoList` — 年报系列
- 以及更多模块（详见 `references/api_docs.md`）

## 接口文档

完整的接口字段定义、请求/响应格式、测试环境说明，参见 `references/api_docs.md`。

## 使用建议

1. **开发联调阶段**：使用 `--env test` 验证字段结构和解析逻辑。
2. **真实数据查询**：使用 `--env prod` 查询真实企业数据，需确保有生产环境调用权限。
3. **大数据量模块**：`AnnRepPaidInInfoList`、`AnnRepSubInfoList`、`OrgShareInfoList` 等可能包含大量条目，建议先使用 `--summary` 查看统计，再针对性提取特定模块。
4. **无数据模块**：返回 `(无数据)` 表示该企业无对应记录（如无失信、无被执行、无股权冻结等），属于正常情况。

## 脚本参数说明

```
--code, -c    统一社会信用代码（必填，18位）
--env, -e     环境：test 或 prod（默认 test）
--module, -m  指定输出模块（默认输出 OrgInfo + 统计概览）
--summary, -s 仅输出模块统计
--output, -o  保存原始响应 JSON 到文件
```
