#!/usr/bin/env python3
"""
切换 OpenClaw 默认模型
用法:
  python set_default.py aicodewith/claude-sonnet-4-6
  python set_default.py kimi-plan/kimi-k2.5
  python set_default.py --show   # 显示当前默认模型
"""
import json, sys, os, re, argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def resolve_path(p):
    return os.path.expanduser(p)

def load_openclaw(path):
    with open(path, "rb") as f:
        raw = f.read()
    enc = "utf-8-sig" if raw.startswith(b'\xef\xbb\xbf') else "utf-8"
    text = raw.decode(enc)
    qclaw_lines = {}
    def replace_qclaw_line(m):
        key = f"__QCLAW_LINE_{len(qclaw_lines)}__"
        qclaw_lines[key] = m.group(0)
        return f'  "{key}": null,'
    cleaned = re.sub(r'^\s*\\"[^\n]+$', replace_qclaw_line, text, flags=re.MULTILINE)
    # 清理控制字符
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', cleaned)
    data = json.loads(cleaned)
    return data, enc, qclaw_lines

def save_openclaw(path, data, enc, qclaw_lines):
    new_json = json.dumps(data, indent=2, ensure_ascii=False)
    for key, original in qclaw_lines.items():
        new_json = new_json.replace(f'  "{key}": null', original.strip())
    with open(path, "wb") as f:
        f.write(new_json.encode(enc))

def main():
    parser = argparse.ArgumentParser(description="切换 OpenClaw 默认模型")
    parser.add_argument("model", nargs="?", help="模型，格式：provider/model-id")
    parser.add_argument("--show", action="store_true", help="显示当前默认模型")
    args = parser.parse_args()

    cfg = load_config()
    openclaw_path = resolve_path(cfg["openclaw_config"])
    data, enc, qclaw_lines = load_openclaw(openclaw_path)

    current = data.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "未设置")

    if args.show or not args.model:
        print(f"当前默认模型: {current}")
        return

    model_str = args.model
    if "/" not in model_str:
        print(f"[ERROR] 格式错误，请使用 provider/model-id，例如: aicodewith/claude-sonnet-4-6")
        sys.exit(1)

    provider, model_id = model_str.split("/", 1)

    # 验证 provider 和模型存在
    providers = data.get("models", {}).get("providers", {})
    if provider not in providers:
        print(f"[ERROR] provider '{provider}' 不存在，可用: {list(providers.keys())}")
        sys.exit(1)

    models = [m["id"] for m in providers[provider].get("models", [])]
    if model_id not in models:
        print(f"[ERROR] 模型 '{model_id}' 不在 provider '{provider}' 中")
        print(f"可用模型: {', '.join(models[:10])}{'...' if len(models)>10 else ''}")
        sys.exit(1)

    data.setdefault("agents", {}).setdefault("defaults", {}).setdefault("model", {})["primary"] = model_str
    save_openclaw(openclaw_path, data, enc, qclaw_lines)
    print(f"✓ 默认模型已切换: {current} → {model_str}")
    print(f"  重启 QClaw 后生效。")

if __name__ == "__main__":
    main()
