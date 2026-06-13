#!/usr/bin/env python3
"""
AiCodeWith 模型列表查询
用法:
  python list_models.py                  # 按厂商分组展示
  python list_models.py --json           # 原始 JSON 输出
  python list_models.py --filter claude  # 按关键词过滤
"""
import json, sys, os, urllib.request, urllib.error, argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_models(cfg):
    url = f"{cfg['base_url'].rstrip('/')}/models"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {cfg['api_key']}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(f"[ERROR] 无法连接 API: {e}", file=sys.stderr)
        sys.exit(1)

def group_by_family(models):
    families = {}
    prefix_map = [
        ("claude",     "Claude (Anthropic)"),
        ("gpt",        "GPT (OpenAI)"),
        ("gemini",     "Gemini (Google)"),
        ("deepseek",   "DeepSeek"),
        ("kimi",       "Kimi (Moonshot)"),
        ("qwen",       "Qwen (Alibaba)"),
        ("qwq",        "QwQ (Alibaba)"),
        ("glm",        "GLM (Zhipu)"),
        ("minimax",    "MiniMax"),
        ("mimo",       "MiMo (Xiaomi)"),
        ("seed",       "Seed (ByteDance)"),
        ("longcat",    "Longcat"),
    ]
    others = []
    for m in models:
        mid = m["id"].lower()
        placed = False
        for prefix, label in prefix_map:
            if mid.startswith(prefix):
                families.setdefault(label, []).append(m["id"])
                placed = True
                break
        if not placed:
            others.append(m["id"])
    if others:
        families["其他"] = others
    return families

def main():
    parser = argparse.ArgumentParser(description="查询 AiCodeWith 可用模型")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    parser.add_argument("--filter", default="", help="按关键词过滤模型 ID")
    args = parser.parse_args()

    cfg = load_config()
    data = fetch_models(cfg)
    models = data.get("data", [])

    if args.filter:
        models = [m for m in models if args.filter.lower() in m["id"].lower()]

    if args.json:
        print(json.dumps(models, indent=2, ensure_ascii=False))
        return

    groups = group_by_family(models)
    total = sum(len(v) for v in groups.values())
    print(f"\nAiCodeWith 可用模型（共 {total} 个）")
    print(f"API: {cfg['base_url']}\n")
    for family, ids in groups.items():
        print(f"【{family}】")
        for mid in ids:
            print(f"  {mid}")
        print()

if __name__ == "__main__":
    main()
