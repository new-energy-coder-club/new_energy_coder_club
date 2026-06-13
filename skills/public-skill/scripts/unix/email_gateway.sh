#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROUTER_JS="${SCRIPT_DIR}/../router.cjs"

if ! command -v node >/dev/null 2>&1; then
  echo '{"success":false,"error_code":2,"message":"未检测到 node，无法运行 public-skill 平台公邮路由"}'
  exit 1
fi

exec node "${ROUTER_JS}" "$@"
