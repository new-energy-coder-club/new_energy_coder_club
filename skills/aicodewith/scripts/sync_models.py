#!/usr/bin/env python3
"""
同步 AiCodeWith 最新模型列表到 OpenClaw 配置
用法:
  python sync_models.py              # 同步并写入 openclaw.json
  python sync_models.py --dry-run    # 预览变更，不写入

原理:
  1. 从 API 拉取最新模型列表
  2. 构建 aicodewith provider 配置块
  3. 合并到 openclaw.json 的 models.providers 中
  4. 保留文件其他配置不变
"""
import json, sys, os, re, urllib.request, urllib.error, argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

REASONING_PATTERNS = [
    "deepseek-r1",
    "kimi-k2-thinking",
    "-thinking",
    "qwq-",
]

MAX_TOKENS_MAP = {
    "claude-opus":  32000,
    "claude":       32000,
    "gpt-5":        32000,
    "gemini":       32000,
    "deepseek-r1":  32000,
    "kimi-k2":      32000,
    "qwen3-235b":   32000,
    "qwen3.5":      32000,
    "qwen3-coder":  32000,
    "minimax-m2.5": 32000,
    "glm-5":        32000,
}
DEFAULT_MAX_TOKENS = 16000

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def resolve_path(p):
    return os.path.expanduser(p)

def fetch_models(cfg):
    url = f"{cfg['base_url'].rstrip('/')}/models"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {cfg['api_key']}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(f"[ERROR] 无法连接 API: {e}", file=sys.stderr)
        sys.exit(1)

def is_reasoning(model_id):
    mid = model_id.lower()
    return any(p in mid for p in REASONING_PATTERNS)

def get_max_tokens(model_id):
    mid = model_id.lower()
    for prefix, val in MAX_TOKENS_MAP.items():
        if mid.startswith(prefix):
            return val
    return DEFAULT_MAX_TOKENS

def build_model_entry(model_id):
    entry = {
        "id": model_id,
        "name": model_id,
        "contextWindow": 200000,
        "maxTokens": get_max_tokens(model_id),
    }
    if is_reasoning(model_id):
        entry["reasoning"] = True
    return entry

def build_provider(cfg, model_ids):
    return {
        "baseUrl": cfg["base_url"],
        "apiKey": cfg["api_key"],
        "api": "openai-completions",
        "models": [build_model_entry(mid) for mid in model_ids]
    }

def load_openclaw(path):
    """读取 openclaw.json，返回 (raw_text, data, encoding, qclaw_lines)"""
    with open(path, "rb") as f:
        raw = f.read()
    enc = "utf-8-sig" if raw.startswith(b'\xef\xbb\xbf') else "utf-8"
    text = raw.decode(enc)

    # 步骤1：移除 QClaw 专有行（以 \" 开头的转义行）
    qclaw_lines = {}
    def replace_qclaw_line(m):
        key = f"__QCLAW_LINE_{len(qclaw_lines)}__"
        qclaw_lines[key] = m.group(0)
        return f'  "{key}": null,'
    cleaned = re.sub(r'^\s*\\"[^\n]+$', replace_qclaw_line, text, flags=re.MULTILINE)

    # 步骤2：清理字符串值中的控制字符（agent name 等乱码字段）
    # 将 JSON 字符串中的非法控制字符替换为 ?
    def sanitize_ctrl(s):
        return re.sub(r'(?<=: ")([^"\\]*(\\.[^"\\]*)*?)(?=")',
                      lambda m: re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '?', m.group(0)),
                      s)
    cleaned = sanitize_ctrl(cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[WARN] JSON 解析失败（{e}），尝试更激进的清理...")
        # 更激进：删除所有控制字符
        cleaned2 = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', cleaned)
        try:
            data = json.loads(cleaned2)
        except json.JSONDecodeError as e2:
            print(f"[ERROR] 仍然失败: {e2}", file=sys.stderr)
            return text, None, enc, qclaw_lines

    return text, data, enc, qclaw_lines

def save_openclaw(path, text, data, enc, qclaw_lines):
    """将修改后的 data 写回文件，还原 QClaw 专有行"""
    # 序列化修改后的 JSON（带占位符）
    new_json = json.dumps(data, indent=2, ensure_ascii=False)

    # 还原 QClaw 专有行
    for key, original in qclaw_lines.items():
        new_json = new_json.replace(f'  "{key}": null', original.strip())

    with open(path, "wb") as f:
        f.write(new_json.encode(enc))

def diff_models(old_ids, new_ids):
    added = set(new_ids) - set(old_ids)
    removed = set(old_ids) - set(new_ids)
    return sorted(added), sorted(removed)

def main():
    parser = argparse.ArgumentParser(description="同步 AiCodeWith 模型到 OpenClaw")
    parser.add_argument("--dry-run", action="store_true", help="预览变更，不写入文件")
    args = parser.parse_args()

    cfg = load_config()
    openclaw_path = resolve_path(cfg["openclaw_config"])
    provider_name = cfg["provider_name"]

    print(f"[1/4] 拉取模型列表 from {cfg['base_url']} ...")
    raw_data = fetch_models(cfg)
    new_model_ids = [m["id"] for m in raw_data.get("data", [])]
    print(f"      获取到 {len(new_model_ids)} 个模型")

    print(f"[2/4] 读取配置 {openclaw_path} ...")
    text, data, enc, qclaw_lines = load_openclaw(openclaw_path)

    if data is None:
        print("[ERROR] 无法解析 openclaw.json，请检查文件格式", file=sys.stderr)
        sys.exit(1)

    print(f"[3/4] 对比变更 ...")
    providers = data.setdefault("models", {}).setdefault("providers", {})
    old_provider = providers.get(provider_name, {})
    old_model_ids = [m["id"] for m in old_provider.get("models", [])]

    added, removed = diff_models(old_model_ids, new_model_ids)
    if added:
        print(f"      + 新增 {len(added)} 个: {', '.join(added[:5])}{'...' if len(added)>5 else ''}")
    if removed:
        print(f"      - 移除 {len(removed)} 个: {', '.join(removed[:5])}{'...' if len(removed)>5 else ''}")
    if not added and not removed:
        print(f"      无变更（共 {len(new_model_ids)} 个模型）")

    if args.dry_run:
        print("\n[dry-run] 预览新 provider 配置:")
        new_provider = build_provider(cfg, new_model_ids)
        print(json.dumps({provider_name: new_provider}, indent=2, ensure_ascii=False)[:2000])
        print("\n[dry-run] 未写入文件。")
        return

    print(f"[4/4] 写入配置 ...")
    providers[provider_name] = build_provider(cfg, new_model_ids)
    save_openclaw(openclaw_path, text, data, enc, qclaw_lines)
    print(f"      完成！{provider_name} provider 已更新（{len(new_model_ids)} 个模型）")
    print(f"\n✓ 重启 QClaw 后生效。")

if __name__ == "__main__":
    main()
