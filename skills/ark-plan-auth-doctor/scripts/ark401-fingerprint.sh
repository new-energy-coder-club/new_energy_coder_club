#!/usr/bin/env bash
# ARK Agent Plan / Coding Plan 401 指纹诊断
# 用法: ark401-fingerprint.sh <ark-api-key> [model]
#   ARK_REGION 环境变量可切换区域,默认 cn-beijing
set -u

KEY="${1:-}"
MODEL="${2:-ark-code-latest}"
REGION="${ARK_REGION:-cn-beijing}"
BASE="https://ark.${REGION}.volces.com"
TMPBODY="$(mktemp 2>/dev/null || echo /tmp/.ark401_body_$$)"

if [[ -z "$KEY" ]]; then
  echo "用法: $0 <ark-api-key> [model]" >&2
  echo "  ARK_REGION=ap-southeast 可切国际站(默认 cn-beijing)" >&2
  exit 2
fi

mask() { local s="$1"; echo "${s:0:8}...${s: -6}"; }

req() {
  local name="$1" url="$2" auth="${3:-__none__}"
  local args=(-sS -o "$TMPBODY" -w "%{http_code}" --max-time 30 -X POST "$url"
    -H "Content-Type: application/json"
    -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":5}")
  if [[ "$auth" != "__none__" ]]; then
    args+=(-H "Authorization: $auth")
  fi
  local code
  code=$(curl "${args[@]}" 2>/dev/null)
  local msg
  msg=$(tr -d '\n\r' < "$TMPBODY" | head -c 260)
  printf "%-14s HTTP %-3s %s\n" "$name" "$code" "$msg"
}

echo "== ARK Plan 401 指纹诊断 =="
echo "Key: $(mask "$KEY")   Base: $BASE   Model: $MODEL"
echo ""
req "正确路径plan" "$BASE/api/plan/v3/chat/completions" "Bearer $KEY"
req "错误路径api"  "$BASE/api/v3/chat/completions"      "Bearer $KEY"
req "无Auth头"     "$BASE/api/plan/v3/chat/completions"
req "缺Bearer前缀" "$BASE/api/plan/v3/chat/completions" "$KEY"
req "伪造Key"      "$BASE/api/plan/v3/chat/completions" "Bearer ark-$(printf '0%.0s' {1..8})-$(printf '0%.0s' {1..4})-$(printf '0%.0s' {1..4})-$(printf '0%.0s' {1..4})-$(printf '0%.0s' {1..12})-$(printf '0%.0s' {1..5})"
echo ""
echo "== 判读 =="
echo "正确路径=200:"
echo "  → Key 有效。拿用户客户端的报错文案对照指纹表:"
echo "    大写'The API key...missing or invalid'+大写'Request id' ⇒ Base URL 缺少 /plan(最高频)"
echo "    小写'the API key...'                                    ⇒ 认证头没发出去/格式错"
echo "正确路径=401 'The API key doesn't exist.':"
echo "  → Key 已删除/轮换/区域不符,去控制台重建后全量替换"
rm -f "$TMPBODY"
