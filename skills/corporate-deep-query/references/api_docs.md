# TrinaPower getCorporateDeepInfo API 文档

## 接口地址

| 环境 | URL |
|------|-----|
| 测试 | `https://apigw-test.trinapower.com/csde-contract-center-api/V1.0.0.0/test/napi/getCorporateDeepInfo` |
| 生产 | `https://apigw.trinablue.com/csde-contract-center-api/V1.0.0.0/prod/napi/getCorporateDeepInfo` |

## 请求方式

- Method: `POST`
- Content-Type: `application/json`

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `uniformSocialCreditCode` | string | 是 | 统一社会信用代码（18位） |

### 请求示例

```json
{
  "uniformSocialCreditCode": "91320411MA1MXKRA7R"
}
```

## 响应结构

顶层为网关包装，业务数据在 `data.responsePlainText` 中（JSON 字符串）。

### 网关层

| 字段 | 说明 |
|------|------|
| `success` | 网关是否成功 |
| `bizcode` | 业务码（10000 为成功） |
| `bizmsg` | 业务消息 |
| `data.responsePlainText` | 嵌套的业务 JSON 字符串 |

### 业务层主要模块

| 模块名 | 说明 | 常见条数 |
|--------|------|---------|
| `OrgInfo` | 企业照面信息（单条） | 1 |
| `OrgShareInfoList` | 股东信息列表 | 数条至数十条 |
| `SharePersonalInfoList` | 高管/董监高信息 | 数条 |
| `AlterationInfoList` | 工商变更记录 | 数条至数十条 |
| `LrInvestmentInfoList` | 法人对外投资 | 数条至数十条 |
| `LrServiceInfoList` | 法人其他任职信息 | 数条至数十条 |
| `OrgInvestmentInfoList` | 企业对外投资 | 数条至数十条 |
| `PledgedEquitiesInfoList` | 股权出质信息 | 数条 |
| `PleEquLogoutInfoList` | 股权出质注销信息 | 数条 |
| `BreakFaithExecutorInfoList` | 失信被执行人 | 数条 |
| `JudicialExecutorInfoList` | 被执行人信息 | 数条 |
| `AdmPenalInfoList` | 行政处罚 | 数条 |
| `AbnormalInfoList` | 经营异常名录 | 数条 |
| `AnnRepBasInfoList` | 年报-基本信息 | 数年 |
| `AnnRepInsInfoList` | 年报-社保信息 | 数年 |
| `AnnRepInvInfoList` | 年报-对外投资 | 数条至数十条 |
| `AnnRepPaidInInfoList` | 年报-实缴出资 | 数条至数十条 |
| `AnnRepSubInfoList` | 年报-认缴出资 | 数条至数十条 |
| `AnnRepModInfoList` | 年报-修改信息 | 数条 |
| `FinalCaseInfoList` | 终本案件 | 数条 |
| `StockFreezeInfoList` | 股权冻结 | 数条 |
| `ISPCheckInfoList` | 抽查检查 | 数条 |
| `CancelBaseInfoList` | 简易注销-基本信息 | 数条 |
| `CancelDissInfoList` | 简易注销-异议信息 | 数条 |
| `ListedStockBaseInfoList` | 上市股票基本信息 | 数条 |
| `ListedCompanyBaseInfoList` | 上市公司基本信息 | 数条 |
| `ListedComExInfoList` | 上市公司高管信息 | 数条 |
| `ShareHolderTopTenList` | 上市公司十大股东 | 数条 |
| `JudgAssBaseInfoList` | 司法协助基本信息 | 数条 |
| `JudgAssDetailList` | 司法协助详情 | 数条 |
| `JudgAssChangeInfoList` | 司法协助变更信息 | 数条 |
| `MovMorBasInfoList` | 动产抵押-基本信息 | 数条 |
| `MovMorAltInfoList` | 动产抵押-变更信息 | 数条 |
| `MovMorLogoutInfoList` | 动产抵押-注销信息 | 数条 |
| `MovMorGuaCreInfoList` | 动产抵押-被担保主债权 | 数条 |
| `MovMorGuarantyInfoList` | 动产抵押-抵押物信息 | 数条 |
| `MovMorPawnorInfoList` | 动产抵押-抵押人信息 | 数条 |
| `MovMorRegInfoList` | 动产抵押-登记信息 | 数条 |
| `OrgClearInfoList` | 清算信息 | 数条 |
| `OrgBranchInfoList` | 分支机构信息 | 数条 |
| `RelBreFaiExeInfoList` | 关联失信被执行人 | 数条 |
| `RelJudExeInfoList` | 关联被执行人 | 数条 |
| `SerIllegalInfoList` | 严重违法 | 数条 |

### OrgInfo 企业照面信息字段

| 字段 | 说明 |
|------|------|
| `OrganizationName` | 企业名称 |
| `UniformSocialCreditCode` | 统一社会信用代码 |
| `IndustryName` | 国民经济行业名称 |
| `IndustryCode` | 国民经济行业代码 |
| `LrName` | 法定代表人姓名 |
| `RegisteredCapital` | 注册资本（万元） |
| `EstablishDate` | 成立日期 |
| `OrganizationState` | 经营状态 |
| `Addr` | 注册地址 |
| `OperateBusinessScope` | 经营范围 |
| `UsedName` | 曾用名 |
| `OrganizationNature` | 企业(机构)类型 |
| `RegOrganization` | 登记机关 |
| `RegisOrgProvince` | 所在省份 |
| `RegisOrgCity` | 所在城市 |
| `RegisOrgDistrict` | 所在区/县 |
| `Telephone` | 联系电话 |
| `Email` | 邮箱 |
| `Currency` | 币种 |
| `PaidInCapital` | 实收资本 |
| `GSGM` | 员工人数 |
| `ApprDate` | 核准日期 |
| `OperateStart` | 经营期限自 |
| `OperateEnd` | 经营期限至 |
| `CancelDate` | 注销日期 |
| `RevokeDate` | 吊销日期 |

### 测试环境说明

测试环境返回的是 **Mock 数据**（固定返回"湖南省广浩宠物用品有限公司"的样板数据），不根据输入的真实统一社会信用代码查询真实企业信息。这属于测试环境的正常行为，用于对接开发验证字段格式和结构。

生产环境返回真实数据。
