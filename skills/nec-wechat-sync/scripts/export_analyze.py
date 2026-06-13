#!/usr/bin/env python3
"""
NEC WeChat Group Sync & Analyze Script
Usage:
    python export_analyze.py export "群名称" --output-dir DIR
    python export_analyze.py analyze chat.md members.json --output record.md
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_wechat_cli(args: list[str]) -> str:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    cmd = ["wechat-cli"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    if result.returncode != 0 and "已导出到" not in result.stderr:
        print("Error:", result.stderr, file=sys.stderr)
        raise RuntimeError(f"wechat-cli failed: {cmd}")
    return result.stdout + result.stderr


def export_chat(group_name: str, output_dir: str, limit: int = 5000):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    chat_md = out / f"chat_{group_name}.md"
    members_json = out / f"members_{group_name}.json"

    # Export markdown
    run_wechat_cli([
        "export", group_name,
        "--format", "markdown",
        "--output", str(chat_md),
        "--limit", str(limit)
    ])
    print(f"[OK] Chat exported: {chat_md}")

    # Export members
    run_wechat_cli([
        "members", group_name,
        "--format", "json"
    ])
    # members outputs to stdout, capture it properly
    members_text = run_wechat_cli(["members", group_name, "--format", "json"])
    with open(members_json, "w", encoding="utf-8") as f:
        f.write(members_text)
    print(f"[OK] Members exported: {members_json}")
    return chat_md, members_json


def parse_chat_md(md_path: str):
    """Extract basic stats from markdown export."""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Header metadata
    group_name = re.search(r"# 聊天记录: (.+)", text)
    msg_count = re.search(r"\*\*消息数量:\*\* (\d+)", text)
    time_range = re.search(r"\*\*时间范围:\*\* (.+)", text)
    export_time = re.search(r"\*\*导出时间:\*\* (.+)", text)

    # Count messages per sender
    sender_pattern = re.compile(r"- \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\] ([^:]+):")
    senders = {}
    for m in sender_pattern.finditer(text):
        s = m.group(1).strip()
        senders[s] = senders.get(s, 0) + 1

    # Extract dates
    dates = re.findall(r"- \[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}\]", text)
    date_set = sorted(set(dates))

    return {
        "group_name": group_name.group(1) if group_name else "Unknown",
        "msg_count": int(msg_count.group(1)) if msg_count else 0,
        "time_range": time_range.group(1) if time_range else "",
        "export_time": export_time.group(1) if export_time else datetime.now().isoformat(),
        "senders": dict(sorted(senders.items(), key=lambda x: -x[1])[:20]),
        "date_span": f"{date_set[0]} ~ {date_set[-1]}" if date_set else "",
        "active_days": len(date_set),
    }


def parse_members_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    members = []
    for m in data.get("members", []):
        name = m.get("remark") or m.get("display_name") or m.get("nick_name") or ""
        members.append({
            "username": m.get("username", ""),
            "name": name,
            "nick_name": m.get("nick_name", ""),
        })
    return {
        "group": data.get("group", ""),
        "member_count": data.get("member_count", 0),
        "owner": data.get("owner", ""),
        "members": members,
    }


def generate_record(chat_md: str, members_json: str, output_md: str):
    chat_info = parse_chat_md(chat_md)
    mem_info = parse_members_json(members_json)

    lines = [
        f"# 群聊分析记录：{chat_info['group_name']}",
        "",
        "## 元信息",
        "| 项目 | 内容 |",
        "|------|------|",
        f"| 群名 | {chat_info['group_name']} |",
        f"| 群ID | {mem_info.get('group', '')} |",
        f"| 群主 | {mem_info['owner']} |",
        f"| 成员数 | {mem_info['member_count']} |",
        f"| 消息量 | {chat_info['msg_count']} |",
        f"| 时间跨度 | {chat_info['date_span']} |",
        f"| 活跃天数 | {chat_info['active_days']} |",
        f"| 导出时间 | {chat_info['export_time']} |",
        f"| 分析版本 | v1.0 |",
        "",
        "## 成员列表",
        "| 序号 | 昵称 | 备注/群昵称 |",
        "|------|------|-------------|",
    ]
    for i, m in enumerate(mem_info["members"][:50], 1):
        lines.append(f"| {i} | {m['nick_name']} | {m['name']} |")

    lines += [
        "",
        "## 高频发言成员 (Top 20)",
        "| 排名 | 昵称 | 发言次数 |",
        "|------|------|----------|",
    ]
    for i, (name, cnt) in enumerate(chat_info["senders"].items(), 1):
        lines.append(f"| {i} | {name} | {cnt} |")

    lines += [
        "",
        "## 原始文件路径",
        f"- 聊天记录: `{chat_md}`",
        f"- 成员列表: `{members_json}`",
        "",
        "---",
        "> 本文件由 nec-wechat-sync Skill 自动生成，供 NEC-Claw / openClaw 飞书机器人读取。",
    ]

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Record generated: {output_md}")


def main():
    parser = argparse.ArgumentParser(description="NEC WeChat Sync")
    sub = parser.add_subparsers(dest="cmd")

    p_export = sub.add_parser("export", help="Export chat and members")
    p_export.add_argument("group_name")
    p_export.add_argument("--output-dir", default=r"D:\NEC-Claw\docs\wechat-analysis")
    p_export.add_argument("--limit", type=int, default=5000)

    p_analyze = sub.add_parser("analyze", help="Analyze exported files")
    p_analyze.add_argument("chat_md")
    p_analyze.add_argument("members_json")
    p_analyze.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.cmd == "export":
        export_chat(args.group_name, args.output_dir, args.limit)
    elif args.cmd == "analyze":
        generate_record(args.chat_md, args.members_json, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
