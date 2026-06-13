#!/usr/bin/env python3
"""
TrinaPower Corporate Deep Info Query Script
Supports test and production environments.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

ENVIRONMENTS = {
    "test": "https://apigw-test.trinapower.com/csde-contract-center-api/V1.0.0.0/test/napi/getCorporateDeepInfo",
    "prod": "https://apigw.trinablue.com/csde-contract-center-api/V1.0.0.0/prod/napi/getCorporateDeepInfo",
}

MODULE_LABELS = {
    "OrgInfo": "企业照面信息",
    "OrgShareInfoList": "股东信息",
    "SharePersonalInfoList": "高管信息",
    "AlterationInfoList": "工商变更记录",
    "LrInvestmentInfoList": "法人对外投资",
    "LrServiceInfoList": "法人任职信息",
    "OrgInvestmentInfoList": "企业对外投资",
    "PledgedEquitiesInfoList": "股权出质",
    "PleEquLogoutInfoList": "股权出质注销",
    "BreakFaithExecutorInfoList": "失信被执行人",
    "JudicialExecutorInfoList": "被执行人",
    "AdmPenalInfoList": "行政处罚",
    "AbnormalInfoList": "经营异常",
    "AnnRepBasInfoList": "年报-基本信息",
    "AnnRepInsInfoList": "年报-社保信息",
    "AnnRepInvInfoList": "年报-对外投资",
    "AnnRepPaidInInfoList": "年报-实缴出资",
    "AnnRepSubInfoList": "年报-认缴出资",
    "AnnRepModInfoList": "年报-修改信息",
    "FinalCaseInfoList": "终本案件",
    "StockFreezeInfoList": "股权冻结",
    "ISPCheckInfoList": "抽查检查",
    "CancelBaseInfoList": "简易注销-基本信息",
    "CancelDissInfoList": "简易注销-异议信息",
    "ListedStockBaseInfoList": "上市股票基本信息",
    "ListedCompanyBaseInfoList": "上市公司基本信息",
    "ListedComExInfoList": "上市公司高管信息",
    "ShareHolderTopTenList": "上市公司十大股东",
    "JudgAssBaseInfoList": "司法协助基本信息",
    "JudgAssDetailList": "司法协助详情",
    "JudgAssChangeInfoList": "司法协助变更信息",
    "MovMorBasInfoList": "动产抵押-基本信息",
    "MovMorAltInfoList": "动产抵押-变更信息",
    "MovMorLogoutInfoList": "动产抵押-注销信息",
    "MovMorGuaCreInfoList": "动产抵押-被担保主债权",
    "MovMorGuarantyInfoList": "动产抵押-抵押物信息",
    "MovMorPawnorInfoList": "动产抵押-抵押人信息",
    "MovMorRegInfoList": "动产抵押-登记信息",
    "OrgClearInfoList": "清算信息",
    "OrgBranchInfoList": "分支机构信息",
    "RelBreFaiExeInfoList": "关联失信被执行人",
    "RelJudExeInfoList": "关联被执行人",
    "SerIllegalInfoList": "严重违法",
}


def fetch(usc_code: str, env: str) -> dict:
    url = ENVIRONMENTS.get(env)
    if not url:
        raise ValueError(f"Unknown environment: {env}. Choose from {list(ENVIRONMENTS.keys())}")

    payload = json.dumps({"uniformSocialCreditCode": usc_code}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "corporate-deep-query/1.0",
    }

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e
    except Exception as e:
        raise RuntimeError(f"Request failed: {e}") from e


def parse_response(raw: dict) -> dict:
    if not raw.get("success"):
        raise RuntimeError(f"Gateway error: bizcode={raw.get('bizcode')}, bizmsg={raw.get('bizmsg')}")

    data = raw.get("data", {})
    plain = data.get("responsePlainText", "{}")
    return json.loads(plain)


def print_org_info(info: dict):
    keys = [
        ("OrganizationName", "企业名称"),
        ("UniformSocialCreditCode", "统一社会信用代码"),
        ("IndustryName", "所属行业"),
        ("IndustryCode", "行业代码"),
        ("LrName", "法定代表人"),
        ("RegisteredCapital", "注册资本(万元)"),
        ("EstablishDate", "成立日期"),
        ("OrganizationState", "经营状态"),
        ("Addr", "注册地址"),
        ("UsedName", "曾用名"),
    ]
    for k, label in keys:
        val = info.get(k, "")
        if val:
            print(f"{label}: {val}")


def print_module_list(data: dict, module: str):
    items = data.get(module, [])
    label = MODULE_LABELS.get(module, module)
    print(f"\n=== {label}（{len(items)} 条）===")
    if not items:
        print("(无数据)")
        return

    for i, item in enumerate(items, 1):
        print(f"\n{i}.")
        for k, v in item.items():
            if v is not None and v != "":
                print(f"   {k}: {v}")


def print_summary(data: dict):
    print("=== 数据模块统计 ===")
    for key, label in MODULE_LABELS.items():
        if key == "OrgInfo":
            continue
        items = data.get(key, [])
        if isinstance(items, list):
            print(f"{label}: {len(items)} 条")


def main():
    parser = argparse.ArgumentParser(description="Query corporate deep info via TrinaPower API")
    parser.add_argument("--code", "-c", required=True, help="统一社会信用代码")
    parser.add_argument("--env", "-e", choices=["test", "prod"], default="test", help="环境: test 或 prod")
    parser.add_argument("--module", "-m", help="指定输出模块（如 OrgInfo, OrgShareInfoList）")
    parser.add_argument("--summary", "-s", action="store_true", help="仅输出模块统计")
    parser.add_argument("--output", "-o", help="保存原始响应 JSON 到文件")
    args = parser.parse_args()

    try:
        raw = fetch(args.code, args.env)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        print(f"Raw response saved to: {args.output}")

    try:
        data = parse_response(raw)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        org = data.get("OrgInfo", {})
        print(f"企业名称: {org.get('OrganizationName', '-')}")
        print(f"统一社会信用代码: {org.get('UniformSocialCreditCode', '-')}")
        print_summary(data)
        return

    if args.module:
        if args.module == "OrgInfo":
            print("=== 企业照面信息 ===")
            print_org_info(data.get("OrgInfo", {}))
        else:
            print_module_list(data, args.module)
        return

    # Default: print OrgInfo + summary
    print("=== 企业照面信息 ===")
    print_org_info(data.get("OrgInfo", {}))
    print_summary(data)


if __name__ == "__main__":
    main()
