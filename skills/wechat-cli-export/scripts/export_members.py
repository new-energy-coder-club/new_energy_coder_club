#!/usr/bin/env python3
"""
WeChat CLI 群成员导出脚本
自动修复 Windows GBK 编码问题，导出三字段 CSV + 完整 JSON
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path


def find_wechat_cli():
    """查找 wechat-cli 可执行文件路径"""
    # 常见安装位置
    candidates = [
        Path.home() / "AppData" / "Local" / "python" / "pythoncore-3.14-64" / "Scripts" / "wechat-cli.exe",
        Path.home() / "AppData" / "Roaming" / "Python" / "Python314" / "Scripts" / "wechat-cli.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python314" / "Scripts" / "wechat-cli.exe",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    # 尝试 PATH 查找
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        exe = Path(path_dir) / "wechat-cli.exe"
        if exe.exists():
            return str(exe)
    return "wechat-cli"


def run_wechat_cli(group_name: str):
    """调用 wechat-cli members，返回解析后的 dict"""
    wechat_cli = find_wechat_cli()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = [wechat_cli, "members", group_name]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    if result.returncode != 0:
        # 尝试用 gbk 解码 stderr（Windows 控制台默认编码）
        stderr = result.stderr
        if not stderr and result.stdout:
            # 有时错误混在 stdout 中
            try:
                json.loads(result.stdout)
            except json.JSONDecodeError:
                stderr = result.stdout
        raise RuntimeError(f"wechat-cli failed (code={result.returncode}): {stderr[:500]}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        # 可能是编码问题，尝试 gbk 解码原始字节
        raw_stdout = result.stdout.encode("utf-8", errors="replace")
        try:
            fixed = raw_stdout.decode("gbk", errors="replace")
            # 去掉替换字符后重试
            clean = fixed.replace("\ufffd", "")
            return json.loads(clean)
        except Exception:
            raise RuntimeError(f"Invalid JSON output: {e}")


def export_csv(data: dict, output_path: Path):
    """导出三字段 CSV"""
    members = data.get("members", [])
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "群昵称(nick_name)", "备注(remark)", "微信号(username)"])
        for i, m in enumerate(members, 1):
            writer.writerow([
                i,
                m.get("nick_name", ""),
                m.get("remark", ""),
                m.get("username", ""),
            ])


def export_json(data: dict, output_path: Path):
    """导出完整 JSON"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="导出微信群成员列表")
    parser.add_argument("group_name", help="群名称（如：26常工院NEC-RC主赛）")
    parser.add_argument("-o", "--output-dir", default=str(Path.home()), help="输出目录（默认：用户主目录）")
    parser.add_argument("--csv-only", action="store_true", help="仅导出 CSV")
    parser.add_argument("--json-only", action="store_true", help="仅导出 JSON")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = args.group_name.replace("/", "_").replace("\\", "_")
    csv_path = output_dir / f"群成员_{safe_name}.csv"
    json_path = output_dir / f"members_{safe_name}.json"

    print(f"正在导出群: {args.group_name}", file=sys.stderr)
    data = run_wechat_cli(args.group_name)

    group = data.get("group", args.group_name)
    count = data.get("member_count", 0)
    owner = data.get("owner", "N/A")

    if not args.json_only:
        export_csv(data, csv_path)
        print(f"[CSV] {csv_path}", file=sys.stderr)

    if not args.csv_only:
        export_json(data, json_path)
        print(f"[JSON] {json_path}", file=sys.stderr)

    # 输出摘要到 stdout（JSON，方便其他工具解析）
    summary = {
        "group": group,
        "member_count": count,
        "owner": owner,
        "csv_path": str(csv_path) if not args.json_only else None,
        "json_path": str(json_path) if not args.csv_only else None,
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
