#!/usr/bin/env bash
# get-token.sh — 从凭证托管服务获取腾讯会议 access_token
#
# 用法:
#   token=$(bash get-token.sh)
#   export TENCENT_MEETING_TOKEN="$token"
#
# Token 由本地代理服务自动注入 JWT，无需手动传入

set -euo pipefail

# 远程 API 基础地址（BUILD_ENV=test 时走测试环境，其他情况走现网）
if [ "$BUILD_ENV" = "test" ]; then
  REMOTE_BASE_URL="https://jprx.sparta.html5.qq.com"
else
  REMOTE_BASE_URL="https://jprx.m.qq.com"
fi

# ── 解析本地代理端口 ─────────────────────────────────────────────────────────

PROXY_PORT="${AUTH_GATEWAY_PORT:-19000}"
PROXY_BASE_URL="http://localhost:${PROXY_PORT}"

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

# ── 主逻辑 ────────────────────────────────────────────────────────────────────

PLATFORM="${CREDENTIAL_PLATFORM:-tencent_meeting}"
BODY="{\"platform\":\"${PLATFORM}\"}"
REMOTE_URL="${REMOTE_BASE_URL}/data/4164/forward"

# 发送请求，将响应体和状态码分别写入临时文件（避免子 shell 变量丢失问题）
tmp_body=$(mktemp)
trap "rm -f '$tmp_body'" EXIT

HTTP_STATUS=$(curl -s -o "$tmp_body" -w "%{http_code}" \
  --connect-timeout 5 --max-time 10 \
  -X POST "${PROXY_BASE_URL}/proxy/api" \
  -H "Remote-URL: ${REMOTE_URL}" \
  -H "Content-Type: application/json" \
  -d "$BODY")

response=$(cat "$tmp_body")

if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "ERROR: HTTP ${HTTP_STATUS}，请先在集成面板中完成腾讯会议授权" >&2
  exit 1
fi

# 解析网关层 ret
ret=$(json_extract "$response" '.ret')
if [[ "$ret" != "0" ]]; then
  echo "ERROR: ret=${ret}，请先在集成面板中完成腾讯会议授权" >&2
  exit 1
fi

# 提取 access_token
access_token=$(json_extract "$response" '.data.resp.data.access_token')

if [[ -z "$access_token" || "$access_token" == "null" ]]; then
  echo "ERROR: 未获取到 access_token，请先在集成面板中完成腾讯会议授权" >&2
  exit 1
fi

printf '%s' "$access_token"
