#!/usr/bin/env python3
"""
天气顾问 — 工具脚本
功能: now, outfit, alert

用法:
    python3 weather_advisor_tool.py now [args]    # 查看天气
    python3 weather_advisor_tool.py outfit [args]    # 穿衣建议
    python3 weather_advisor_tool.py alert [args]    # 天气预警
"""

import sys, json, os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
REF_URLS = ["https://openweathermap.org/", "https://github.com/topics/weather-api", "https://www.xiaohongshu.com/explore/weather-outfit"]

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    data_file = os.path.join(DATA_DIR, "weather_advisor_data.json")
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"records": [], "created": datetime.now().isoformat(), "tool": "weather-advisor"}

def save_data(data):
    ensure_data_dir()
    data_file = os.path.join(DATA_DIR, "weather_advisor_data.json")
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now(args):
    """查看天气"""
    data = load_data()
    record = {
        "timestamp": datetime.now().isoformat(),
        "command": "now",
        "input": " ".join(args) if args else "",
        "status": "completed"
    }
    data["records"].append(record)
    save_data(data)
    return {
        "status": "success",
        "command": "now",
        "message": "now完成",
        "record": record,
        "total_records": len(data["records"]),
        "reference_urls": REF_URLS[:3]
    }


def outfit(args):
    """穿衣建议"""
    data = load_data()
    record = {
        "timestamp": datetime.now().isoformat(),
        "command": "outfit",
        "input": " ".join(args) if args else "",
        "status": "completed"
    }
    data["records"].append(record)
    save_data(data)
    return {
        "status": "success",
        "command": "outfit",
        "message": "outfit完成",
        "record": record,
        "total_records": len(data["records"]),
        "reference_urls": REF_URLS[:3]
    }


def alert(args):
    """天气预警"""
    data = load_data()
    record = {
        "timestamp": datetime.now().isoformat(),
        "command": "alert",
        "input": " ".join(args) if args else "",
        "status": "completed"
    }
    data["records"].append(record)
    save_data(data)
    return {
        "status": "success",
        "command": "alert",
        "message": "alert完成",
        "record": record,
        "total_records": len(data["records"]),
        "reference_urls": REF_URLS[:3]
    }


def main():
    cmds = ["now", "outfit", "alert"]
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(json.dumps({
            "error": f"用法: weather_advisor_tool.py <{','.join(cmds)}> [args]",
            "available_commands": {"now": "查看天气", "outfit": "穿衣建议", "alert": "天气预警"},
            "tool": "weather-advisor",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    result = globals()[cmd](args)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
