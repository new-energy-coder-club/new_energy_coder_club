#!/usr/bin/env bash
# get-token.sh — 从凭证网关获取邮箱授权码并写入 imap-smtp-email/.env
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SKILL_DIR}/.env"

TOKEN=""
EMAIL=""
PLATFORM=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --token) [[ $# -lt 2 ]] && { echo "错误: --token 需要提供值" >&2; exit 1; }; TOKEN="$2"; shift 2 ;;
    --email) [[ $# -lt 2 ]] && { echo "错误: --email 需要提供值" >&2; exit 1; }; EMAIL="$2"; shift 2 ;;
    --platform) [[ $# -lt 2 ]] && { echo "错误: --platform 需要提供值" >&2; exit 1; }; PLATFORM="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# BUILD_ENV=test 时走测试环境，其他情况走现网
if [ "$BUILD_ENV" = "test" ]; then
  REMOTE_BASE_URL="https://jprx.sparta.html5.qq.com"
else
  REMOTE_BASE_URL="https://jprx.m.qq.com"
fi
PROXY_PORT="${AUTH_GATEWAY_PORT:-19000}"
PROXY_BASE_URL="http://localhost:${PROXY_PORT}"
REMOTE_URL="${REMOTE_BASE_URL}/data/4164/forward"
CHECKED_PLATFORMS='["163_mail","qq_mail","gmail","outlook","sina_mail","sohu_mail"]'

emit_json() {
  local success="$1"
  local error_code="$2"
  local message="$3"
  local extra_json="${4:-{}}"
  SUCCESS_VALUE="$success" ERROR_CODE_VALUE="$error_code" MESSAGE_VALUE="$message" EXTRA_JSON_VALUE="$extra_json" node - <<'NODE'
const rawExtra = String(process.env.EXTRA_JSON_VALUE || '{}').trim();
let extra;
try {
  extra = JSON.parse(rawExtra);
} catch (error) {
  if (rawExtra.endsWith('}}')) {
    extra = JSON.parse(rawExtra.slice(0, -1));
  } else {
    throw error;
  }
}
const payload = {
  success: process.env.SUCCESS_VALUE === 'true',
  message: process.env.MESSAGE_VALUE || '',
  ...extra,
};
if (process.env.ERROR_CODE_VALUE !== '') {
  payload.error_code = Number(process.env.ERROR_CODE_VALUE);
}
process.stdout.write(`${JSON.stringify(payload)}\n`);
NODE
}

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
const parts = p.replace(/^\./, '').split('.');
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

infer_servers() {
  local domain="$1"
  case "$domain" in
    163.com)         IMAP_HOST="imap.163.com";         SMTP_HOST="smtp.163.com";         SMTP_PORT="465"; SMTP_SECURE="true" ;;
    vip.163.com)     IMAP_HOST="imap.vip.163.com";     SMTP_HOST="smtp.vip.163.com";     SMTP_PORT="465"; SMTP_SECURE="true" ;;
    126.com)         IMAP_HOST="imap.126.com";         SMTP_HOST="smtp.126.com";         SMTP_PORT="465"; SMTP_SECURE="true" ;;
    vip.126.com)     IMAP_HOST="imap.vip.126.com";     SMTP_HOST="smtp.vip.126.com";     SMTP_PORT="465"; SMTP_SECURE="true" ;;
    188.com)         IMAP_HOST="imap.188.com";         SMTP_HOST="smtp.188.com";         SMTP_PORT="465"; SMTP_SECURE="true" ;;
    vip.188.com)     IMAP_HOST="imap.vip.188.com";     SMTP_HOST="smtp.vip.188.com";     SMTP_PORT="465"; SMTP_SECURE="true" ;;
    yeah.net)        IMAP_HOST="imap.yeah.net";        SMTP_HOST="smtp.yeah.net";        SMTP_PORT="465"; SMTP_SECURE="true" ;;
    gmail.com)       IMAP_HOST="imap.gmail.com";       SMTP_HOST="smtp.gmail.com";       SMTP_PORT="587"; SMTP_SECURE="false" ;;
    outlook.com)     IMAP_HOST="outlook.office365.com"; SMTP_HOST="smtp-mail.outlook.com"; SMTP_PORT="587"; SMTP_SECURE="false" ;;
    hotmail.com)     IMAP_HOST="outlook.office365.com"; SMTP_HOST="smtp-mail.outlook.com"; SMTP_PORT="587"; SMTP_SECURE="false" ;;
    live.com)        IMAP_HOST="outlook.office365.com"; SMTP_HOST="smtp-mail.outlook.com"; SMTP_PORT="587"; SMTP_SECURE="false" ;;
    live.cn)         IMAP_HOST="outlook.office365.com"; SMTP_HOST="smtp-mail.outlook.com"; SMTP_PORT="587"; SMTP_SECURE="false" ;;
    qq.com)          IMAP_HOST="imap.qq.com";          SMTP_HOST="smtp.qq.com";          SMTP_PORT="465"; SMTP_SECURE="true" ;;
    foxmail.com)     IMAP_HOST="imap.qq.com";          SMTP_HOST="smtp.qq.com";          SMTP_PORT="465"; SMTP_SECURE="true" ;;
    vip.qq.com)      IMAP_HOST="imap.vip.qq.com";      SMTP_HOST="smtp.vip.qq.com";      SMTP_PORT="465"; SMTP_SECURE="true" ;;
    yahoo.com)       IMAP_HOST="imap.mail.yahoo.com"; SMTP_HOST="smtp.mail.yahoo.com";   SMTP_PORT="465"; SMTP_SECURE="true" ;;
    sina.com)        IMAP_HOST="imap.sina.com";        SMTP_HOST="smtp.sina.com";        SMTP_PORT="465"; SMTP_SECURE="true" ;;
    sina.cn)         IMAP_HOST="imap.sina.com";        SMTP_HOST="smtp.sina.com";        SMTP_PORT="465"; SMTP_SECURE="true" ;;
    vip.sina.com)    IMAP_HOST="imap.vip.sina.com";    SMTP_HOST="smtp.vip.sina.com";    SMTP_PORT="465"; SMTP_SECURE="true" ;;
    sohu.com)        IMAP_HOST="imap.sohu.com";        SMTP_HOST="smtp.sohu.com";        SMTP_PORT="465"; SMTP_SECURE="true" ;;
    139.com)         IMAP_HOST="imap.139.com";         SMTP_HOST="smtp.139.com";         SMTP_PORT="465"; SMTP_SECURE="true" ;;
    exmail.qq.com)   IMAP_HOST="imap.exmail.qq.com";   SMTP_HOST="smtp.exmail.qq.com";   SMTP_PORT="465"; SMTP_SECURE="true" ;;
    aliyun.com)      IMAP_HOST="imap.aliyun.com";      SMTP_HOST="smtp.aliyun.com";      SMTP_PORT="465"; SMTP_SECURE="true" ;;
    *)
      return 1 ;;
  esac
  return 0
}

write_env() {
  local email_address="$1"
  local access_token="$2"
  local token_source="$3"
  local email_domain="${email_address##*@}"
  cat > "$ENV_FILE" <<EOF
# Provider hint
EMAIL_PROVIDER_HINT=${email_domain}

# IMAP Configuration
IMAP_HOST=${IMAP_HOST}
IMAP_PORT=993
IMAP_USER=${email_address}
IMAP_PASS=${access_token}
IMAP_TLS=true
IMAP_REJECT_UNAUTHORIZED=true
IMAP_MAILBOX=INBOX
IMAP_CONN_TIMEOUT_MS=20000
IMAP_AUTH_TIMEOUT_MS=15000
IMAP_SOCKET_TIMEOUT_MS=30000
IMAP_CONNECTION_RETRIES=2
IMAP_RETRY_DELAY_MS=1500
IMAP_KEEPALIVE_INTERVAL_MS=10000
IMAP_IDLE_INTERVAL_MS=300000

# SMTP Configuration
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=${SMTP_PORT}
SMTP_SECURE=${SMTP_SECURE}
SMTP_USER=${email_address}
SMTP_PASS=${access_token}
SMTP_FROM=${email_address}
SMTP_REJECT_UNAUTHORIZED=true
SMTP_CONNECTION_TIMEOUT_MS=30000
SMTP_GREETING_TIMEOUT_MS=30000
SMTP_SOCKET_TIMEOUT_MS=60000
SMTP_DNS_TIMEOUT_MS=30000
SMTP_CONNECTION_RETRIES=2
SMTP_RETRY_DELAY_MS=1500

# File access whitelist
ALLOWED_READ_DIRS=$HOME/Downloads,$HOME/Documents
ALLOWED_WRITE_DIRS=$HOME/Downloads

# Token source (used to decide whether runtime auto-refresh may overwrite this file)
TOKEN_SOURCE=${token_source}
EOF
  chmod 600 "$ENV_FILE"
}

platform_from_domain() {
  local domain="$1"
  case "$domain" in
    163.com|vip.163.com|126.com|vip.126.com|188.com|vip.188.com|yeah.net)
      echo "163_mail" ;;
    qq.com|foxmail.com|vip.qq.com|exmail.qq.com)
      echo "qq_mail" ;;
    gmail.com)
      echo "gmail" ;;
    outlook.com|hotmail.com|live.com|live.cn)
      echo "outlook" ;;
    sina.com|sina.cn|vip.sina.com)
      echo "sina_mail" ;;
    sohu.com)
      echo "sohu_mail" ;;
    *)
      echo "" ;;
  esac
}

FAILURE_RECORDS=()
record_failure() {
  local platform="$1"
  local error_code="$2"
  local message="$3"
  FAILURE_RECORDS+=("${platform}"$'\t'"${error_code}"$'\t'"${message}")
}

emit_best_failure_and_exit() {
  local platform=""
  local error_code="3"
  local message="未从凭证服务获取到可用的个人邮箱授权信息，请先登录并接通邮箱能力，或改用 setup.sh 手动配置。"

  if [[ ${#FAILURE_RECORDS[@]} -gt 0 ]]; then
    local chosen="${FAILURE_RECORDS[0]}"
    for item in "${FAILURE_RECORDS[@]}"; do
      IFS=$'\t' read -r current_platform current_code current_message <<< "$item"
      if [[ "$current_code" == "21004" ]]; then
        chosen="$item"
        break
      fi
    done
    IFS=$'\t' read -r platform error_code message <<< "$chosen"
  fi

  emit_json false "$error_code" "$message" "{\"checked_platforms\":${CHECKED_PLATFORMS},\"source\":\"credential_service\",\"platform\":\"${platform}\"}"
  exit 1
}

if [[ -n "$TOKEN" || -n "$EMAIL" ]]; then
  if [[ -z "$TOKEN" || -z "$EMAIL" ]]; then
    emit_json false 1 "--token 和 --email 必须同时提供" "{\"mode\":\"manual-token\"}"
    exit 1
  fi
  if [[ "$TOKEN" =~ [[:space:]] ]]; then
    emit_json false 1 "授权码不能包含空格或换行符" "{\"mode\":\"manual-token\"}"
    exit 1
  fi
  if [[ "$EMAIL" != *@* ]]; then
    emit_json false 1 "邮箱地址格式无效" "{\"mode\":\"manual-token\"}"
    exit 1
  fi
  EMAIL=$(echo "$EMAIL" | tr -d '[:space:]')
  domain="${EMAIL##*@}"
  if ! infer_servers "$domain"; then
    emit_json false 1 "当前 get-token.sh 不支持自动推断域名 ${domain}，请改用 setup.sh 或手工写入 .env" "{\"mode\":\"manual-token\"}"
    exit 1
  fi
  write_env "$EMAIL" "$TOKEN" "manual_token"
  emit_json true "" "已写入个人邮箱凭证" "{\"env_path\":\"${ENV_FILE}\",\"mode\":\"manual-token\"}"
  exit 0
fi

# ── 模式二：指定 platform 拉取凭证 ──
if [[ -n "$PLATFORM" ]]; then
  BODY="{\"platform\":\"${PLATFORM}\"}"
  tmp_body=$(mktemp)
  set +e
  HTTP_STATUS=$(curl -s -o "$tmp_body" -w "%{http_code}" \
    -X POST "${PROXY_BASE_URL}/proxy/api" \
    -H "Remote-URL: ${REMOTE_URL}" \
    -H "Content-Type: application/json" \
    -d "$BODY")
  CURL_EXIT=$?
  set -e
  response=$(cat "$tmp_body")
  rm -f "$tmp_body"

  if [[ $CURL_EXIT -ne 0 ]]; then
    emit_json false 999 "请求凭证服务失败，请检查本地代理或登录态。" "{\"platform\":\"${PLATFORM}\",\"mode\":\"platform-specific\"}"
    exit 1
  fi
  if [[ "$HTTP_STATUS" != "200" ]]; then
    emit_json false 999 "凭证服务 HTTP 请求失败，状态码: ${HTTP_STATUS}" "{\"platform\":\"${PLATFORM}\",\"mode\":\"platform-specific\"}"
    exit 1
  fi

  ret=$(json_extract "$response" '.ret' | tr -d '\r')
  if [[ "$ret" != "0" ]]; then
    emit_json false 999 "凭证服务网关返回异常，ret=${ret}" "{\"platform\":\"${PLATFORM}\",\"mode\":\"platform-specific\"}"
    exit 1
  fi

  common_code=$(json_extract "$response" '.data.resp.common.code' | tr -d '\r')
  common_message=$(json_extract "$response" '.data.resp.common.message' | tr -d '\r')
  if [[ -z "$common_code" || "$common_code" == "null" ]]; then
    common_code="999"
  fi
  if [[ "$common_code" != "0" ]]; then
    emit_json false "$common_code" "${common_message:-凭证服务返回失败}" "{\"platform\":\"${PLATFORM}\",\"mode\":\"platform-specific\"}"
    exit 1
  fi

  access_token=$(json_extract "$response" '.data.resp.data.access_token' | tr -d '\r')
  email_address=$(json_extract "$response" '.data.resp.data.extra_data.email_address' | tr -d '\r')
  if [[ -z "$access_token" || "$access_token" == "null" || -z "$email_address" || "$email_address" == "null" ]]; then
    emit_json false 3 "凭证服务未返回可用的邮箱地址或授权码" "{\"platform\":\"${PLATFORM}\",\"mode\":\"platform-specific\"}"
    exit 1
  fi

  domain="${email_address##*@}"
  if ! infer_servers "$domain"; then
    emit_json false 1 "当前 get-token.sh 不支持自动推断域名 ${domain}，请改用 setup.sh 或手工写入 .env" "{\"platform\":\"${PLATFORM}\",\"mode\":\"platform-specific\"}"
    exit 1
  fi

  write_env "$email_address" "$access_token" "credential_service"
  emit_json true "" "已从凭证服务刷新个人邮箱凭证" "{\"env_path\":\"${ENV_FILE}\",\"mode\":\"platform-specific\",\"platform\":\"${PLATFORM}\",\"email\":\"${email_address}\"}"
  exit 0
fi

# ── 模式三：自动遍历所有平台 ──
for platform in 163_mail qq_mail gmail outlook sina_mail sohu_mail; do
  BODY="{\"platform\":\"${platform}\"}"
  tmp_body=$(mktemp)
  set +e
  HTTP_STATUS=$(curl -s -o "$tmp_body" -w "%{http_code}" \
    -X POST "${PROXY_BASE_URL}/proxy/api" \
    -H "Remote-URL: ${REMOTE_URL}" \
    -H "Content-Type: application/json" \
    -d "$BODY")
  CURL_EXIT=$?
  set -e
  response=$(cat "$tmp_body")
  rm -f "$tmp_body"

  if [[ $CURL_EXIT -ne 0 ]]; then
    record_failure "$platform" 999 "请求凭证服务失败，请检查本地代理或登录态。"
    continue
  fi

  if [[ "$HTTP_STATUS" != "200" ]]; then
    record_failure "$platform" 999 "凭证服务 HTTP 请求失败，状态码: ${HTTP_STATUS}"
    continue
  fi

  ret=$(json_extract "$response" '.ret' | tr -d '\r')
  if [[ "$ret" != "0" ]]; then
    record_failure "$platform" 999 "凭证服务网关返回异常，ret=${ret}"
    continue
  fi

  common_code=$(json_extract "$response" '.data.resp.common.code' | tr -d '\r')
  common_message=$(json_extract "$response" '.data.resp.common.message' | tr -d '\r')
  if [[ -z "$common_code" || "$common_code" == "null" ]]; then
    common_code="999"
  fi
  if [[ "$common_code" != "0" ]]; then
    record_failure "$platform" "$common_code" "${common_message:-凭证服务返回失败}"
    continue
  fi

  access_token=$(json_extract "$response" '.data.resp.data.access_token' | tr -d '\r')
  email_address=$(json_extract "$response" '.data.resp.data.extra_data.email_address' | tr -d '\r')
  if [[ -z "$access_token" || "$access_token" == "null" || -z "$email_address" || "$email_address" == "null" ]]; then
    record_failure "$platform" 3 "凭证服务未返回可用的邮箱地址或授权码"
    continue
  fi

  domain="${email_address##*@}"
  expected_platform=$(platform_from_domain "$domain")
  if [[ -n "$expected_platform" && "$expected_platform" != "$platform" ]]; then
    record_failure "$platform" 3 "凭证服务返回的邮箱 ${email_address} 与平台 ${platform} 不匹配"
    continue
  fi

  if ! infer_servers "$domain"; then
    record_failure "$platform" 1 "当前 get-token.sh 不支持自动推断域名 ${domain}，请改用 setup.sh 或手工写入 .env"
    continue
  fi

  write_env "$email_address" "$access_token" "credential_service"
  emit_json true "" "已从凭证服务刷新个人邮箱凭证" "{\"env_path\":\"${ENV_FILE}\",\"mode\":\"credential-service\",\"platform\":\"${platform}\",\"email\":\"${email_address}\"}"
  exit 0
done

emit_best_failure_and_exit
