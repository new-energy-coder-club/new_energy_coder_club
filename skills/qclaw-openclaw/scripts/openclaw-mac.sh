#!/usr/bin/env bash
set -euo pipefail

# QClaw OpenClaw CLI wrapper (macOS)
#
# 从 ~/.qclaw/qclaw.json 读取运行时路径，通过独立 Node.js 二进制执行 openclaw 命令。
#
# 用法:
#   bash scripts/openclaw-mac.sh <command> [args...]
#   bash scripts/openclaw-mac.sh config get gateway.port
#   bash scripts/openclaw-mac.sh cron list
#   bash scripts/openclaw-mac.sh skills list

PREFIX="[qclaw-cli]"
META_FILE="${HOME}/.qclaw/qclaw.json"

# ============================================================
# 读取 QClaw 元信息
# ============================================================

if [ ! -f "${META_FILE}" ]; then
  echo "${PREFIX} 错误: 元信息文件不存在: ${META_FILE}"
  echo "${PREFIX} 请先启动 QClaw 桌面应用"
  exit 1
fi

# 使用 python3 解析 JSON（macOS 自带）
NODE_BINARY=$(python3 -c "import sys,json; print(json.load(sys.stdin)['cli']['nodeBinary'])" < "${META_FILE}")
OPENCLAW_MJS=$(python3 -c "import sys,json; print(json.load(sys.stdin)['cli']['openclawMjs'])" < "${META_FILE}")
STATE_DIR=$(python3 -c "import sys,json; print(json.load(sys.stdin)['stateDir'])" < "${META_FILE}")
CONFIG_PATH=$(python3 -c "import sys,json; print(json.load(sys.stdin)['configPath'])" < "${META_FILE}")

# 验证路径有效性
if [ ! -f "${NODE_BINARY}" ]; then
  echo "${PREFIX} 错误: Node 二进制不存在: ${NODE_BINARY}"
  echo "${PREFIX} 请重启 QClaw 应用以更新元信息"
  exit 1
fi

if [ ! -f "${OPENCLAW_MJS}" ]; then
  echo "${PREFIX} 错误: openclaw.mjs 不存在: ${OPENCLAW_MJS}"
  echo "${PREFIX} 请重启 QClaw 应用以更新元信息"
  exit 1
fi

# ============================================================
# 环境变量注入
# ============================================================

export NODE_OPTIONS="--no-warnings"
export OPENCLAW_NIX_MODE=1
export OPENCLAW_STATE_DIR="${STATE_DIR}"
export OPENCLAW_CONFIG_PATH="${CONFIG_PATH}"

# ============================================================
# 执行 openclaw CLI
# ============================================================

exec "${NODE_BINARY}" "${OPENCLAW_MJS}" "$@"
