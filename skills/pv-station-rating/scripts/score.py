#!/usr/bin/env python3
"""工商业光伏电站分层分级评分（两步走）

用法 1（命令行 + JSON）：
    python score.py --data project.json
    python score.py --data project.json --report-md report.md

用法 2（命令行 + 内联 JSON）：
    python score.py --json '{"name":"测试","grades":{...}}'

用法 3（Python 库）：
    from score import score_project
    result = score_project(data_dict)
    print(result["report_text"])

用法 4（读模板示例，自检）：
    python score.py --selftest

数据 schema 见 references/data-schema.md。
"""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional

GRADE_PCT = {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25}
GRADE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3}
ORDER_GRADE = {v: k for k, v in GRADE_ORDER.items()}

DIM_WEIGHTS = {
    "d1_enterprise":  ("维度1 企业性质/规模",  2.5),
    "d2_region":      ("维度2 省份区域",        2.0),
    "d3_self_use":    ("维度3 自发自用比例",    1.5),
    "d4_materials":   ("维度4 材料齐全性",      1.0),
    "d5_finance":     ("维度5 财务状况",        2.0),
    "d6_industry":    ("维度6 行业稳定性",      1.0),
}

D5_SUB = {
    "d5a_finance_health": ("5a 整体财务健康度",       0.8),
    "d5b_pv_share":       ("5b 光伏电费/总电费",     0.5),
    "d5c_revenue_cover":  ("5c 营收/光伏电费",       0.4),
    "d5d_profit_cover":   ("5d 净利润/光伏电费",     0.3),
}

IRR_BASELINE = {
    "A": (6.5, 7.5, "低风险优质资产"),
    "B": (7.0, 8.0, "中低风险"),
    "C": (7.5, 8.5, "中等风险"),
    "D": (9.0, 10.0, "高风险"),
}

SCORE_BAND = [
    (8.0, 10.0, "A"),
    (6.0, 7.99, "B"),
    (4.0, 5.99, "C"),
    (0.0, 3.99, "D"),
]


@dataclass
class AdjustmentItem:
    name: str
    score_delta: float
    irr_delta_pct: float
    note: str = ""


def normalize_grade(g) -> str:
    if g is None:
        raise ValueError("grade 不能为空")
    s = str(g).strip().upper()
    if s not in GRADE_PCT:
        raise ValueError(f"非法等级 {g!r}，必须是 A/B/C/D")
    return s


def expand_grades(grades: dict) -> dict:
    """允许调用方只传 d5_finance 一个总评，自动展开成 5a/5b/5c/5d。"""
    out = {k: normalize_grade(v) for k, v in grades.items() if v is not None}
    if any(k in out for k in D5_SUB):
        for k in D5_SUB:
            if k not in out:
                if "d5_finance" in out:
                    out[k] = out["d5_finance"]
                else:
                    raise ValueError(f"缺少财务子项 {k}（且未提供 d5_finance 兜底）")
    elif "d5_finance" in out:
        for k in D5_SUB:
            out[k] = out["d5_finance"]
    else:
        raise ValueError("必须提供 d5_finance（或 5a/5b/5c/5d 子项）")
    for k in ("d1_enterprise", "d2_region", "d3_self_use", "d4_materials", "d6_industry"):
        if k not in out:
            raise ValueError(f"缺少必填维度 {k}")
    return out


def step1_simple_rating(grades: dict, veto: dict) -> dict:
    """简版：木桶 / 多数 / 一票否决。"""
    six = {
        "d1_enterprise": grades["d1_enterprise"],
        "d2_region":     grades["d2_region"],
        "d3_self_use":   grades["d3_self_use"],
        "d4_materials":  grades["d4_materials"],
        "d5_finance":    grades.get("d5_finance") or _aggregate_d5_grade(grades),
        "d6_industry":   grades["d6_industry"],
    }

    barrel = ORDER_GRADE[max(GRADE_ORDER[g] for g in six.values())]

    counts = {}
    for g in six.values():
        counts[g] = counts.get(g, 0) + 1
    majority = None
    for g, n in counts.items():
        if n >= 4:
            majority = g
            break
    if majority is None:
        finance_g = six["d5_finance"]
        industry_g = six["d6_industry"]
        majority = ORDER_GRADE[max(GRADE_ORDER[finance_g], GRADE_ORDER[industry_g])]
        majority_note = f"无 ≥4 同级，按财务/行业取低 → {majority}"
    else:
        majority_note = f"≥4 个维度同为 {majority}"

    veto_hit = []
    if veto.get("enterprise_d_blacklist") or six["d1_enterprise"] == "D":
        if veto.get("enterprise_d_blacklist"):
            veto_hit.append("企业性质 D（失信/税务/经营异常）")
    if veto.get("finance_d_no_guarantee"):
        veto_hit.append("财务 D 且无强担保")
    if veto.get("materials_d_filing_missing"):
        veto_hit.append("材料 D（备案/接入缺失）")
    if veto.get("industry_d_forbidden") or six["d6_industry"] == "D":
        if veto.get("industry_d_forbidden"):
            veto_hit.append("行业 D（房地产/P2P/教培）")

    final = barrel
    veto_apply = bool(veto_hit)
    if veto_apply:
        final = "D"

    return {
        "per_dim_grades": six,
        "barrel": barrel,
        "majority": majority,
        "majority_note": majority_note,
        "veto_hits": veto_hit,
        "veto_applied": veto_apply,
        "final_grade": final,
        "method_used": "一票否决" if veto_apply else "木桶（默认推荐）",
    }


def _aggregate_d5_grade(grades: dict) -> str:
    """如果只有 5a/5b/5c/5d，简版用 4 子项最低等级当 d5_finance。"""
    sub = [grades[k] for k in D5_SUB if k in grades]
    if not sub:
        raise ValueError("无财务等级")
    return ORDER_GRADE[max(GRADE_ORDER[g] for g in sub)]


def _build_adjustments(adj: dict) -> list[AdjustmentItem]:
    items: list[AdjustmentItem] = []
    if adj.get("long_term_50mw"):
        items.append(AdjustmentItem("长期合作 ≥50MW", +0.5, -0.5))
    elif adj.get("long_term_20mw"):
        items.append(AdjustmentItem("长期合作 ≥20MW", +0.2, -0.2))
    if adj.get("strategic"):
        items.append(AdjustmentItem("战略协同（央国企 / 批量）", +0.1, -0.1))
    if adj.get("storage"):
        items.append(AdjustmentItem("光储协同（储能 ≥10%）", +0.1, -0.1))
    miss = int(adj.get("missing_materials") or 0)
    if miss > 0:
        miss_capped = min(miss, 5)
        items.append(AdjustmentItem(
            f"材料缺失 × {miss_capped}（每项 -0.1，封顶 -0.5）",
            -0.1 * miss_capped, +0.1 * miss_capped,
            note="复杂版分数封顶 -0.5；简版 IRR 封顶 +0.5%",
        ))
    if adj.get("finance_abnormal"):
        items.append(AdjustmentItem("财务异常（亏损 / 现金流为负）", -0.2, +0.2))
    if adj.get("red_zone"):
        items.append(AdjustmentItem("区域红区（电网红色预警）", -0.3, +0.3))
    return items


def step2_weighted_score(grades: dict, adjustments: list[AdjustmentItem]) -> dict:
    dim_scores = {
        "d1_enterprise": GRADE_PCT[grades["d1_enterprise"]] * DIM_WEIGHTS["d1_enterprise"][1],
        "d2_region":     GRADE_PCT[grades["d2_region"]]     * DIM_WEIGHTS["d2_region"][1],
        "d3_self_use":   GRADE_PCT[grades["d3_self_use"]]   * DIM_WEIGHTS["d3_self_use"][1],
        "d4_materials":  GRADE_PCT[grades["d4_materials"]]  * DIM_WEIGHTS["d4_materials"][1],
        "d6_industry":   GRADE_PCT[grades["d6_industry"]]   * DIM_WEIGHTS["d6_industry"][1],
    }
    d5_sub_scores = {
        k: round(GRADE_PCT[grades[k]] * cap, 4)
        for k, (_, cap) in D5_SUB.items()
    }
    dim_scores["d5_finance"] = round(sum(d5_sub_scores.values()), 4)

    base = round(sum(dim_scores.values()), 4)
    adj_total = round(sum(a.score_delta for a in adjustments), 4)
    final = round(max(0.0, min(10.0, base + adj_total)), 4)

    grade = "D"
    for lo, hi, g in SCORE_BAND:
        if lo <= final <= hi:
            grade = g
            break

    return {
        "dim_scores": dim_scores,
        "d5_sub_scores": d5_sub_scores,
        "base_total": base,
        "adjustment_total": adj_total,
        "final_total": final,
        "grade": grade,
    }


def merge_irr(grade: str, adjustments: list[AdjustmentItem]) -> tuple[float, float, float]:
    lo, hi, _ = IRR_BASELINE[grade]
    irr_delta = round(sum(a.irr_delta_pct for a in adjustments), 4)
    return round(lo + irr_delta, 3), round(hi + irr_delta, 3), irr_delta


def score_project(data: dict) -> dict:
    name = data.get("name") or "未命名项目"
    grades = expand_grades(data.get("grades") or {})
    adj_dict = data.get("adjustments") or {}
    veto = data.get("veto") or {}
    adjustments = _build_adjustments(adj_dict)

    s1 = step1_simple_rating(grades, veto)
    s2 = step2_weighted_score(grades, adjustments)

    if s1["veto_applied"]:
        final_grade = "D"
    else:
        final_grade = s2["grade"]

    base_lo, base_hi, _ = IRR_BASELINE[final_grade]
    final_lo, final_hi, irr_delta = merge_irr(final_grade, adjustments)

    risks = []
    for k, g in s1["per_dim_grades"].items():
        if g in ("C", "D"):
            risks.append(f"{DIM_WEIGHTS[k][0]} = {g}")
    if s1["veto_applied"]:
        for v in s1["veto_hits"]:
            risks.append(f"⚠ 一票否决：{v}")

    suggestions = _suggestions(s1, s2, adjustments)

    result = {
        "name": name,
        "grades_used": grades,
        "step1_simple": s1,
        "step2_weighted": s2,
        "adjustments": [asdict(a) for a in adjustments],
        "final_grade": final_grade,
        "irr": {
            "baseline_low": base_lo,
            "baseline_high": base_hi,
            "delta_pct": irr_delta,
            "final_low": final_lo,
            "final_high": final_hi,
            "risk_label": IRR_BASELINE[final_grade][2],
        },
        "risks": risks,
        "suggestions": suggestions,
    }
    result["report_text"] = render_report(result)
    return result


def _suggestions(s1, s2, adjustments):
    out = []
    if s1["veto_applied"]:
        out.append("已触发一票否决：建议直接退案，或要求强担保 / 第三方增信后重审。")
    grades = s1["per_dim_grades"]
    if grades["d4_materials"] in ("C", "D"):
        out.append("材料：补办备案/接入批复/电费账单/负荷曲线，争取升至 B。")
    if grades["d5_finance"] in ("C", "D"):
        out.append("财务：要求母公司担保 / 应收账款保理 / 提高首付比例。")
    if grades["d3_self_use"] == "D":
        out.append("消纳：缩小光伏装机或配套储能至 ≥10%，把消纳率拉回 60-80%。")
    if grades["d2_region"] in ("C", "D"):
        out.append("省份：核查所在区县红黄区状态，准备区域红区加点 0.3% 预案。")
    if not out:
        out.append("六维度均 ≥B，整体优良；按基准 IRR 推进即可。")
    return out


def render_report(r: dict) -> str:
    lines = []
    lines.append(f"# 评级报告 · {r['name']}\n")

    lines.append("## 一、维度等级（含财务子项）")
    pdg = r["step1_simple"]["per_dim_grades"]
    for k, (label, _) in DIM_WEIGHTS.items():
        lines.append(f"- {label}：**{pdg[k]}**")
    lines.append("\n财务子项明细：")
    for k, (label, cap) in D5_SUB.items():
        sub_grade = r["grades_used"][k]
        sub_score = r["step2_weighted"]["d5_sub_scores"][k]
        lines.append(f"  - {label}（满分 {cap}）：{sub_grade} → {sub_score}")
    lines.append("")

    lines.append("## 二、第一步 简版结论")
    s1 = r["step1_simple"]
    lines.append(f"- 木桶原则：**{s1['barrel']}**")
    lines.append(f"- 多数原则：**{s1['majority']}**（{s1['majority_note']}）")
    if s1["veto_hits"]:
        for v in s1["veto_hits"]:
            lines.append(f"- ⚠ 一票否决命中：{v}")
    lines.append(f"- 采用方法：{s1['method_used']}")
    lines.append("")

    lines.append("## 三、第二步 复杂版评分")
    s2 = r["step2_weighted"]
    for k, (label, cap) in DIM_WEIGHTS.items():
        lines.append(f"- {label}（满分 {cap}）：**{s2['dim_scores'][k]}**")
    lines.append(f"- 基础总分：**{s2['base_total']}** / 10")
    if r["adjustments"]:
        lines.append("- 加减分明细：")
        for a in r["adjustments"]:
            sign = "+" if a["score_delta"] >= 0 else ""
            lines.append(f"  - {a['name']}：分数 {sign}{a['score_delta']}，IRR {a['irr_delta_pct']:+}%")
    else:
        lines.append("- 加减分明细：无")
    lines.append(f"- 加减分小计：分数 {s2['adjustment_total']:+}，最终总分 **{s2['final_total']}** / 10")
    lines.append(f"- 复杂版等级：**{s2['grade']}**")
    lines.append("")

    lines.append("## 四、综合等级与基准 IRR")
    lines.append(f"- **综合等级：{r['final_grade']} 级**（{r['irr']['risk_label']}）")
    lines.append(f"- 基准 IRR：{r['irr']['baseline_low']}% - {r['irr']['baseline_high']}%")
    if r['irr']['delta_pct'] != 0:
        lines.append(f"- IRR 调整：{r['irr']['delta_pct']:+}%")
    lines.append(f"- **最终 IRR：{r['irr']['final_low']}% - {r['irr']['final_high']}%**")
    lines.append("")

    lines.append("## 五、风险点")
    if r["risks"]:
        for x in r["risks"]:
            lines.append(f"- {x}")
    else:
        lines.append("- 无显著风险点（六维度均 ≥B）。")
    lines.append("")

    lines.append("## 六、建议")
    for s in r["suggestions"]:
        lines.append(f"- {s}")
    lines.append("\n*最终立项以投资评审会决议为准。*")
    return "\n".join(lines)


SELFTEST_CASES = [
    {
        "name": "示例1：汽车零部件厂",
        "grades": {"d1_enterprise":"A","d2_region":"A","d3_self_use":"A","d4_materials":"A",
                   "d5a_finance_health":"A","d5b_pv_share":"A","d5c_revenue_cover":"A","d5d_profit_cover":"A",
                   "d6_industry":"B"},
        "adjustments": {"long_term_20mw": True},
        "expected_final_total": 9.95, "expected_grade": "A",
        "excel_value": 10.0,
        "note": "Excel 显示 10.0 应为四舍五入；公式精确值为 9.95",
    },
    {
        "name": "示例2：食品加工厂",
        "grades": {"d1_enterprise":"B","d2_region":"B","d3_self_use":"B","d4_materials":"B",
                   "d5a_finance_health":"B","d5b_pv_share":"B","d5c_revenue_cover":"B","d5d_profit_cover":"B",
                   "d6_industry":"B"},
        "expected_final_total": 7.5, "expected_grade": "B",
        "excel_value": 7.5,
        "note": "完全一致（无加减分）",
    },
    {
        "name": "示例3：小型纺织厂",
        "grades": {"d1_enterprise":"C","d2_region":"B","d3_self_use":"C","d4_materials":"C",
                   "d5a_finance_health":"C","d5b_pv_share":"B","d5c_revenue_cover":"C","d5d_profit_cover":"C",
                   "d6_industry":"B"},
        "adjustments": {"missing_materials": 2, "finance_abnormal": True},
        "expected_final_total": 5.475, "expected_grade": "C",
        "excel_value": 5.35,
        "note": "Excel 5.75 应为 5.875（5b=B/0.375 而非 C/0.25）；最终公式 5.475，等级一致",
    },
    {
        "name": "示例4：物流公司",
        "grades": {"d1_enterprise":"B","d2_region":"A","d3_self_use":"C","d4_materials":"A",
                   "d5a_finance_health":"B","d5b_pv_share":"A","d5c_revenue_cover":"A","d5d_profit_cover":"B",
                   "d6_industry":"B"},
        "expected_final_total": 8.1, "expected_grade": "A",
        "excel_value": 7.875,
        "note": "Excel 7.875 漏算 0.225；公式精确 8.1 → 实际应入 A 级而非 B 级",
    },
    {
        "name": "示例5：建材经销商",
        "grades": {"d1_enterprise":"C","d2_region":"C","d3_self_use":"D","d4_materials":"C",
                   "d5a_finance_health":"C","d5b_pv_share":"C","d5c_revenue_cover":"C","d5d_profit_cover":"D",
                   "d6_industry":"D"},
        "adjustments": {"red_zone": True},
        "expected_final_total": 4.0, "expected_grade": "C",
        "excel_value": 4.075,
        "note": "Excel 4.375 与公式 4.3 略差 0.075；最终 4.0，等级一致",
    },
]


def selftest():
    ok = 0
    fail = 0
    print("跑 5 个原表示例做回归（公式精确值 vs Excel 手填值）：\n")
    for case in SELFTEST_CASES:
        r = score_project(case)
        ft = r["step2_weighted"]["final_total"]
        gd = r["step2_weighted"]["grade"]
        passed = abs(ft - case["expected_final_total"]) < 0.01 and gd == case["expected_grade"]
        flag = "OK " if passed else "FAIL"
        print(f"[{flag}] {case['name']:<20s}  公式={ft}/{gd}  Excel={case['excel_value']}  -- {case['note']}")
        if passed:
            ok += 1
        else:
            fail += 1
    print(f"\n合计 {ok} 通过 / {fail} 失败  (公式实现以本脚本为准；Excel 手填值见 examples/example_run.md)")
    return fail == 0


def main():
    p = argparse.ArgumentParser(description="工商业光伏电站分层分级评分")
    p.add_argument("--data", help="项目数据 JSON 文件路径")
    p.add_argument("--json", help="项目数据 JSON 字符串")
    p.add_argument("--report-md", help="把 Markdown 报告写到这里")
    p.add_argument("--report-json", help="把完整结果（含 report_text）写到这里")
    p.add_argument("--selftest", action="store_true", help="跑 5 个原表示例做回归")
    args = p.parse_args()

    if args.selftest:
        ok = selftest()
        sys.exit(0 if ok else 1)

    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif args.json:
        data = json.loads(args.json)
    else:
        p.error("必须提供 --data / --json / --selftest 之一")
        return

    r = score_project(data)
    print(r["report_text"])

    if args.report_md:
        with open(args.report_md, "w", encoding="utf-8") as f:
            f.write(r["report_text"])
    if args.report_json:
        out = {k: v for k, v in r.items() if k != "report_text"}
        out["report_text"] = r["report_text"]
        with open(args.report_json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
