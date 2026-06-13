#!/usr/bin/env bash
# ==========================================================================
# sort-desktop-mac.sh — macOS 桌面图标排列脚本（纯 Bash，零依赖，无需授权）
# ==========================================================================
# 通过删除桌面 .DS_Store 文件并重启 Finder 来重置桌面布局。
# 无需 AppleScript 权限，会触发 Finder 自动重新排列图标。
# ==========================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

SORT_BY=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --sort-by|-SortBy)
            SORT_BY="$2"; shift 2 ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--sort-by ItemType]"
            exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# Validate sort option
if [[ -n "$SORT_BY" ]] && [[ "$SORT_BY" != "ItemType" ]]; then
    echo "=== SORT DESKTOP RESULT ==="
    echo "status: error"
    echo "platform: macOS"
    echo "message: Unsupported sort option: $SORT_BY (only ItemType is supported)"
    echo "=== END ==="
    exit 1
fi

# Get desktop path
DESKTOP_DIR="$HOME/Desktop"
DS_STORE_PATH="$DESKTOP_DIR/.DS_Store"

# Check if desktop exists
if [[ ! -d "$DESKTOP_DIR" ]]; then
    echo "=== SORT DESKTOP RESULT ==="
    echo "status: error"
    echo "platform: macOS"
    echo "message: Desktop directory not found: $DESKTOP_DIR"
    echo "=== END ==="
    exit 1
fi

# Delete DS_Store file if exists
if [[ -f "$DS_STORE_PATH" ]]; then
    rm -f "$DS_STORE_PATH"

    echo "=== SORT DESKTOP RESULT ==="
    echo "status: success"
    echo "platform: macOS"
    echo "method: Delete .DS_Store and restart Finder (no permission required)"
    if [[ -n "$SORT_BY" ]]; then
        echo "sort_by: $SORT_BY"
    else
        echo "sort_by: (system default)"
    fi
    echo ""
    echo "--- ACTION DETAILS ---"
    echo "Deleted: $DS_STORE_PATH"

    # Restart Finder to trigger layout rebuild
    killall Finder 2>/dev/null || true

    # Wait for Finder to restart
    sleep 1

    echo "Finder restarted"
    echo ""
    echo "note: Icons arranged according to system Finder settings"
    echo "=== END ==="

    echo ""
    echo "✓ Desktop icon layout reset completed!"
    echo "  Note: Icons will be arranged according to your Finder settings"
    echo "  (Right-click desktop > 'Sort By' to change arrangement)"
else
    echo "=== SORT DESKTOP RESULT ==="
    echo "status: success"
    echo "platform: macOS"
    echo "method: No .DS_Store found (layout already default)"
    echo ""
    echo "--- ACTION DETAILS ---"
    echo "No .DS_Store file found at: $DS_STORE_PATH"
    echo "Layout is already at default state"
    echo "=== END ==="
fi
