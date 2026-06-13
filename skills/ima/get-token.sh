#!/usr/bin/env bash
# get-token.sh — 获取 IMA OpenAPI 凭证（Client ID + API Key）
#
# 用法:
#   CREDS=$(bash get-token.sh)
#   # 返回 JSON: {"client_id":"...","api_key":"..."}
#
# 支持两种凭证来源（按优先级）：
#   1. 本地代理服务（平台托管模式，AUTH_GATEWAY_PORT 环境变量存在时启用）
#   2. 环境变量 / 配置文件（本地模式）

set -euo pipefail

# ── JSON 解析：优先 jq，fallback 到 node ─────────────────────────────────────

json_extract() {
  local json="$1"
  local path="$2"

  if command -v jq &>/dev/null; then
    echo "$json" | jq -r "$path"
  else
    local node_path
    node_path=$(echo "$path" | node -e "
const p = require('fs').readFileSync('/dev/stdin','utf8').trim();
if (p === '.') { process.stdout.write(''); process.exit(0); }
const parts = p.replace(/^\\./, '').split('.');
process.stdout.write(parts.map(k => '[\"' + k + '\"]').join(''));
")
    echo "$json" | node -e "
const data = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
const val = data${node_path};
if (val === null || val === undefined) console.log('null');
else if (typeof val === 'object') console.log(JSON.stringify(val));
else console.log(val);
"
  fi
}

# ── 输出 JSON 凭证 ────────────────────────────────────────────────────────────

output_credentials() {
  local cid="$1" key="$2"
  if command -v jq &>/dev/null; then
    jq -nc --arg c "$cid" --arg k "$key" '{"client_id":$c,"api_key":$k}'
  elif command -v node &>/dev/null; then
    node -e "process.stdout.write(JSON.stringify({client_id:process.argv[1],api_key:process.argv[2]}))" "$cid" "$key"
  else
    # Fallback: manual JSON — safe for typical credential strings
    printf '{"client_id":"%s","api_key":"%s"}' "$cid" "$key"
  fi
}

# ── 模式 1：本地代理服务（平台托管） ──────────────────────────────────────────

if [[ -n "${AUTH_GATEWAY_PORT:-}" ]]; then
  PROXY_PORT="${AUTH_GATEWAY_PORT}"
  PROXY_BASE_URL="http://localhost:${PROXY_PORT}"

  # BUILD_ENV=test 时走测试环境，其他情况走现网
  if [ "$BUILD_ENV" = "test" ]; then
    REMOTE_BASE_URL="https://jprx.sparta.html5.qq.com"
  else
    REMOTE_BASE_URL="https://jprx.m.qq.com"
  fi

  PLATFORM="${CREDENTIAL_PLATFORM:-ima}"
  BODY="{\"platform\":\"${PLATFORM}\"}"
  REMOTE_URL="${REMOTE_BASE_URL}/data/4164/forward"

  tmp_body=$(mktemp)
  trap "rm -f '$tmp_body'" EXIT

  HTTP_STATUS=$(curl -s -o "$tmp_body" -w "%{http_code}" \
    -X POST "${PROXY_BASE_URL}/proxy/api" \
    -H "Remote-URL: ${REMOTE_URL}" \
    -H "Content-Type: application/json" \
    -d "$BODY")

  response=$(cat "$tmp_body")

  if [[ "$HTTP_STATUS" != "200" ]]; then
    echo "ERROR: HTTP ${HTTP_STATUS}" >&2
    exit 1
  fi

  ret=$(json_extract "$response" '.ret')
  if [[ "$ret" != "0" ]]; then
    echo "ERROR: ret=${ret}" >&2
    exit 1
  fi

  # access_token → api_key, extra_data.client_id → client_id
  api_key=$(json_extract "$response" '.data.resp.data.access_token')
  client_id=$(json_extract "$response" '.data.resp.data.extra_data.client_id')

  if [[ -z "$client_id" || "$client_id" == "null" || -z "$api_key" || "$api_key" == "null" ]]; then
    echo "ERROR: 未获取到 IMA 凭证，请先在集成面板中完成 IMA 授权" >&2
    exit 1
  fi

  output_credentials "$client_id" "$api_key"
  exit 0
fi

# ── 模式 2：环境变量 / 配置文件（本地模式） ──────────────────────────────────

IMA_CLIENT_ID="${IMA_OPENAPI_CLIENTID:-$(cat ~/.config/ima/client_id 2>/dev/null || true)}"
IMA_API_KEY="${IMA_OPENAPI_APIKEY:-$(cat ~/.config/ima/api_key 2>/dev/null || true)}"

if [[ -z "$IMA_CLIENT_ID" || -z "$IMA_API_KEY" ]]; then
  echo "ERROR: 缺少 IMA 凭证。请按以下方式之一配置：" >&2
  echo "  方式 A（配置文件）：mkdir -p ~/.config/ima && echo 'YOUR_ID' > ~/.config/ima/client_id && echo 'YOUR_KEY' > ~/.config/ima/api_key" >&2
  echo "  方式 B（环境变量）：export IMA_OPENAPI_CLIENTID=xxx && export IMA_OPENAPI_APIKEY=yyy" >&2
  exit 1
fi

output_credentials "$IMA_CLIENT_ID" "$IMA_API_KEY"
