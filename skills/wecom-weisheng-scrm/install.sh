#!/usr/bin/env bash
# install.sh — 一键安装 / 卸载微盛企微管家 SCRM skill 到 openclaw
# 注意：本脚本仅适用于 OpenClaw 场景；QClaw 用户请在设置 → 技能管理中直接启用

set -euo pipefail

SKILL_NAME="wecom-weisheng-scrm"
OPENCLAW_SKILLS_DIR="${HOME}/.openclaw/skills"
TARGET_DIR="${OPENCLAW_SKILLS_DIR}/${SKILL_NAME}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "用法: $0 [install|uninstall]"
  echo ""
  echo "  install    将 skill 安装到 ${TARGET_DIR}"
  echo "  uninstall  从 ${TARGET_DIR} 卸载 skill"
  exit 1
}

do_install() {
  if [[ ! -d "${OPENCLAW_SKILLS_DIR}" ]]; then
    echo "错误: openclaw skills 目录不存在: ${OPENCLAW_SKILLS_DIR}"
    exit 1
  fi

  if [[ -L "${TARGET_DIR}" ]]; then
    echo "已存在软链接 ${TARGET_DIR}，跳过安装（如需重装请先卸载）"
    exit 0
  fi

  if [[ -d "${TARGET_DIR}" ]]; then
    echo "警告: ${TARGET_DIR} 已存在（非软链接），请手动确认后再操作"
    exit 1
  fi

  ln -s "${SCRIPT_DIR}" "${TARGET_DIR}"
  echo "✓ 已安装: ${TARGET_DIR} -> ${SCRIPT_DIR}"

  # skill.md 是 openclaw 识别的入口文件，确保顶层有 SKILL.md 软链接
  if [[ ! -f "${SCRIPT_DIR}/SKILL.md" && -f "${SCRIPT_DIR}/skill.md" ]]; then
    ln -s "${SCRIPT_DIR}/skill.md" "${SCRIPT_DIR}/SKILL.md"
    echo "✓ 已创建 SKILL.md 软链接（指向 skill.md）"
  fi
}

do_uninstall() {
  if [[ -L "${TARGET_DIR}" ]]; then
    rm "${TARGET_DIR}"
    echo "✓ 已卸载: ${TARGET_DIR}"
  elif [[ -d "${TARGET_DIR}" ]]; then
    echo "警告: ${TARGET_DIR} 存在但不是软链接，请手动删除"
    exit 1
  else
    echo "未安装，无需卸载"
  fi

  # 清理 SKILL.md 软链接（如果是本脚本创建的）
  if [[ -L "${SCRIPT_DIR}/SKILL.md" ]]; then
    rm "${SCRIPT_DIR}/SKILL.md"
    echo "✓ 已删除 SKILL.md 软链接"
  fi
}

CMD="${1:-}"
case "${CMD}" in
  install)   do_install ;;
  uninstall) do_uninstall ;;
  *)         usage ;;
esac
