#!/usr/bin/env bash
# ============================================================================
# AIPPT Generate Script
# 通过 Auth Gateway 的 aippt 代理调用智绘高迪 Design Agent API
#
# Gateway 会等待上游 SSE 的 started 事件，提取 projectId 后返回 JSON：
#   { success, projectId, sessionIds, workspaceUrl, message }
# 脚本只需解析该 JSON 即可。
# ============================================================================

set -euo pipefail

# ── 参数校验 ──────────────────────────────────────────────────────────────
if [ -z "${PROMPT:-}" ]; then
  echo "❌ 错误: 缺少 PROMPT 环境变量" >&2
  echo "用法: PROMPT='PPT内容描述' bash $0" >&2
  exit 1
fi

# ── 推导 Auth Gateway aippt 代理地址 ──────────────────────────────────────
# QCLAW_LLM_BASE_URL 格式: http://127.0.0.1:{port}/proxy/llm
# 替换 /llm 为 /aippt/agent/run
if [ -z "${QCLAW_LLM_BASE_URL:-}" ]; then
  echo "❌ 错误: QCLAW_LLM_BASE_URL 未设置" >&2
  exit 1
fi

AUTH_GW_BASE="${QCLAW_LLM_BASE_URL%/llm}"
AIPPT_URL="${AUTH_GW_BASE}/aippt/agent/run"

# ── 构建请求 body ────────────────────────────────────────────────────────
# Gateway handler 会自动注入 customModelProvider（含 apiKey）和 taskAgentType
# Skill 脚本只需传 prompt 和可选的 modelId
BODY=$(python3 -c '
import json, os

body = {
    "prompt": os.environ["PROMPT"],
}

print(json.dumps(body, ensure_ascii=False))
')

# ── 获取 API Key（通过 4164 凭证托管接口）──────────────────────────────
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AIPPT_API_KEY=""

if [ -f "${SKILL_DIR}/get-token.sh" ]; then
  AIPPT_API_KEY=$(bash "${SKILL_DIR}/get-token.sh" 2>/dev/null) || true
fi

if [ -z "$AIPPT_API_KEY" ]; then
  echo "❌ 错误: 未获取到 AIPPT API Key，请先在集成面板中完成授权" >&2
  exit 1
fi

echo "📝 开始生成 PPT..."
echo ""

# ── 调用 aippt 代理 ──────────────────────────────────────────────────────
# Gateway 内部处理 SSE，收到 started 事件后返回 JSON 响应
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

HTTP_CODE=$(curl -s -w "%{http_code}" -o "$TMPFILE" \
  -X POST "${AIPPT_URL}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${QCLAW_LLM_API_KEY:-__QCLAW_AUTH_GATEWAY_MANAGED__}" \
  -H "X-API-Key: ${AIPPT_API_KEY}" \
  -H "X-Platform: qclaw" \
  -d "$BODY" \
  --max-time 300)

RESPONSE=$(cat "$TMPFILE")

if [ "$HTTP_CODE" -ne 200 ]; then
  echo "❌ API 请求失败 (HTTP ${HTTP_CODE}):" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

# ── 解析 JSON 响应 ────────────────────────────────────────────────────────
SUCCESS=$(python3 -c "
import json, sys
try:
    d = json.loads(sys.argv[1])
    print('true' if d.get('success') else 'false')
except:
    print('false')
" "$RESPONSE" 2>/dev/null || echo "false")

if [ "$SUCCESS" != "true" ]; then
  echo "❌ 生成失败:" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

# 提取关键字段
RESULT=$(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
print(json.dumps({
    'projectId': d.get('projectId', ''),
    'workspaceUrl': d.get('workspaceUrl', ''),
    'message': d.get('message', ''),
}, indent=2, ensure_ascii=False))
" "$RESPONSE" 2>/dev/null)

PROJECT_ID=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('projectId',''))" "$RESPONSE" 2>/dev/null || echo "")
WORKSPACE_URL=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('workspaceUrl',''))" "$RESPONSE" 2>/dev/null || echo "")

echo "🚀 任务已启动，PPT 正在后台生成中"
echo ""
echo "✅ PPT 生成任务已提交！"
echo ""
echo "结果："
echo "$RESULT"
echo ""
if [ -n "$WORKSPACE_URL" ]; then
  echo "📊 编辑地址: ${WORKSPACE_URL}"
fi
