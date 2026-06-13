#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOLVE_ACCOUNT_JS="${SCRIPT_DIR}/../resolve-account.cjs"

if ! command -v node >/dev/null 2>&1; then
  echo '{"success":false,"error_code":2,"message":"未检测到 node，无法运行 imap-smtp-email 个人邮箱路由"}'
  exit 1
fi

exec node "${RESOLVE_ACCOUNT_JS}" "$@"
