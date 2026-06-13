#!/usr/bin/env bash
# ==========================================================================
# rollback-mac.sh — macOS 文件回撤脚本（纯 Bash，零依赖）
# ==========================================================================
# 读取 organize-mac.sh 生成的 TSV 操作日志，将文件移回原位置。
# 回撤完成后自动清理因撤销而变空的自动创建文件夹。
# ==========================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

usage() {
    cat <<'EOF'
Usage:
  rollback-mac.sh list-logs    --target-dir <DIR>
  rollback-mac.sh rollback-all --log-path <LOG_FILE> [--dry-run]
  rollback-mac.sh rollback-single --log-path <LOG_FILE> --filename <NAME> [--dry-run]
EOF
    exit 1
}

COMMAND=""
LOG_PATH=""
FILE_NAME=""
TARGET_DIR=""
DRY_RUN="false"
# Global temp file for cleanup
_ROLLBACK_TMPFILE=""

cleanup_temp() {
    if [[ -n "$_ROLLBACK_TMPFILE" ]] && [[ -f "$_ROLLBACK_TMPFILE" ]]; then
        rm -f "$_ROLLBACK_TMPFILE"
    fi
}
trap cleanup_temp EXIT

[[ $# -eq 0 ]] && usage

COMMAND="$1"; shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        --log-path)
            LOG_PATH="$2"; shift 2 ;;
        --filename)
            FILE_NAME="$2"; shift 2 ;;
        --target-dir)
            TARGET_DIR="$2"; shift 2 ;;
        --dry-run)
            DRY_RUN="true"; shift ;;
        *)
            echo "Unknown option: $1"; usage ;;
    esac
done

# ---------------------------------------------------------------------------
# Helper: count real (non-hidden, non-system) files in a folder
# ---------------------------------------------------------------------------
count_real_files() {
    local dir="$1"
    local count=0
    for entry in "$dir"/*; do
        [[ -e "$entry" ]] || continue
        local ename
        ename="$(basename "$entry")"
        [[ "$ename" == .* ]] && continue
        [[ "$ename" == "desktop.ini" ]] && continue
        [[ "$ename" == "Thumbs.db" ]] && continue
        count=$((count + 1))
    done
    echo "$count"
}

# ---------------------------------------------------------------------------
# Helper: clean up an empty auto-created folder
# ---------------------------------------------------------------------------
try_clean_folder() {
    local folder_path="$1"
    local folder_name="$2"

    if [[ -d "$folder_path" ]]; then
        local real_files
        real_files="$(count_real_files "$folder_path")"

        if [[ "$real_files" -eq 0 ]]; then
            if [[ "$DRY_RUN" == "false" ]]; then
                # Remove hidden files first
                for hf in "$folder_path"/.*; do
                    [[ -f "$hf" ]] && rm -f "$hf" 2>/dev/null || true
                done
                # Remove visible system files
                rm -f "$folder_path/desktop.ini" "$folder_path/Thumbs.db" "$folder_path/.DS_Store" 2>/dev/null || true
                rmdir "$folder_path" 2>/dev/null || rm -rf "$folder_path" 2>/dev/null || true
            fi
            echo "REMOVED|$folder_name|$folder_path"
        fi
    fi
}

# ---------------------------------------------------------------------------
# list-logs: List available operation logs
# ---------------------------------------------------------------------------
do_list_logs() {
    if [[ -z "$TARGET_DIR" ]]; then
        echo "Error: list-logs requires --target-dir"
        exit 1
    fi

    local resolved_dir
    resolved_dir="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
        echo "Error: Directory does not exist: $TARGET_DIR"
        exit 1
    }

    local log_dir="$resolved_dir/.file_organizer_logs"
    if [[ ! -d "$log_dir" ]]; then
        echo "=== AVAILABLE LOGS ==="
        echo "message: 未找到操作日志目录"
        echo "=== END ==="
        return
    fi

    echo "=== AVAILABLE LOGS ==="

    # Find log files, sort by name (newest first since filenames contain timestamps)
    local found=0
    for f in $(ls -1r "$log_dir"/organize_*.log 2>/dev/null); do
        [[ -f "$f" ]] || continue
        found=1

        local fname
        fname="$(basename "$f")"

        # Read metadata from first line
        local timestamp="unknown"
        local op_count=0

        if head -1 "$f" | grep -q "^#META"; then
            timestamp="$(head -1 "$f" | sed -n 's/.*timestamp=\([^	]*\).*/\1/p')"
        fi

        # Count operation lines (non-comment, non-empty lines)
        op_count="$(grep -cv '^#\|^$' "$f" 2>/dev/null || echo "0")"

        echo "file: $fname"
        echo "  path: $f"
        echo "  timestamp: $timestamp"
        echo "  operations_count: $op_count"
        echo ""
    done

    if [[ $found -eq 0 ]]; then
        echo "message: 未找到任何操作日志"
    fi

    echo "=== END ==="
}

# ---------------------------------------------------------------------------
# rollback-all: Reverse all operations in a log
# ---------------------------------------------------------------------------
do_rollback_all() {
    if [[ -z "$LOG_PATH" ]]; then
        echo "Error: rollback-all requires --log-path"
        exit 1
    fi

    if [[ ! -f "$LOG_PATH" ]]; then
        echo "Error: Log file not found: $LOG_PATH"
        exit 1
    fi

    # Create temp file safely (global var so trap can clean it up)
    _ROLLBACK_TMPFILE=$(mktemp) || {
        echo "Error: Failed to create temp file"
        exit 1
    }

    echo "=== ROLLBACK RESULTS ==="
    echo "rollback_log: $LOG_PATH"
    echo "dry_run: $DRY_RUN"
    echo ""

    # Read operation lines (non-comment lines) into temp file
    : > "$_ROLLBACK_TMPFILE"
    while IFS= read -r line; do
        # Skip comment lines and empty lines
        [[ "$line" == \#* ]] && continue
        [[ -z "$line" ]] && continue
        echo "$line" >> "$_ROLLBACK_TMPFILE"
    done < "$LOG_PATH"

    # Reverse the operations and process them
    # NOTE: avoid pipeline subshell so counters persist
    local restored_count=0
    local failed_count=0
    local reversed_file
    reversed_file=$(mktemp)
    awk '{line[NR]=$0} END {for(i=NR;i>0;i--) print line[i]}' "$_ROLLBACK_TMPFILE" > "$reversed_file"

    echo "--- RESTORED ---"
    while IFS=$'\t' read -r file orig_path dest_path folder method status; do
        # Skip dry_run entries
        [[ "$status" == "dry_run" ]] && continue

        # Check if destination file exists
        if [[ ! -e "$dest_path" ]]; then
            echo "FAILED|$file|目标文件不存在: $dest_path"
            failed_count=$((failed_count + 1))
            continue
        fi

        # Check if original location already has a file
        if [[ -e "$orig_path" ]]; then
            echo "FAILED|$file|原位置已有同名文件: $orig_path"
            failed_count=$((failed_count + 1))
            continue
        fi

        # Perform rollback
        if [[ "$DRY_RUN" == "false" ]]; then
            # Ensure parent directory exists
            local parent_dir
            parent_dir="$(dirname "$orig_path")"
            mkdir -p "$parent_dir"
            mv "$dest_path" "$orig_path"
        fi

        echo "OK|$file|$dest_path|$orig_path"
        restored_count=$((restored_count + 1))
    done < "$reversed_file"
    rm -f "$reversed_file"

    echo ""

    # Clean up empty auto-created folders
    echo "--- CLEANED FOLDERS ---"
    local cleaned_count=0
    while IFS= read -r line; do
        [[ "$line" == \#CREATED_FOLDER* ]] || continue
        IFS=$'\t' read -r _tag folder_name folder_path _created_at <<< "$line"

        local result
        result="$(try_clean_folder "$folder_path" "$folder_name")"
        if [[ -n "$result" ]]; then
            echo "$result"
            cleaned_count=$((cleaned_count + 1))
        fi
    done < "$LOG_PATH"

    echo ""
    echo "--- SUMMARY ---"
    echo "restored: $restored_count"
    echo "failed: $failed_count"
    echo "cleaned_folders: $cleaned_count"
    echo "=== END ==="
}

# ---------------------------------------------------------------------------
# rollback-single: Reverse a single file operation
# ---------------------------------------------------------------------------
do_rollback_single() {
    if [[ -z "$LOG_PATH" ]]; then
        echo "Error: rollback-single requires --log-path"
        exit 1
    fi
    if [[ -z "$FILE_NAME" ]]; then
        echo "Error: rollback-single requires --filename"
        exit 1
    fi
    if [[ ! -f "$LOG_PATH" ]]; then
        echo "Error: Log file not found: $LOG_PATH"
        exit 1
    fi

    echo "=== ROLLBACK SINGLE RESULT ==="
    echo "rollback_log: $LOG_PATH"
    echo "target_file: $FILE_NAME"
    echo "dry_run: $DRY_RUN"
    echo ""

    # Find the matching operation
    local found_line=""
    while IFS= read -r line; do
        [[ "$line" == \#* ]] && continue
        [[ -z "$line" ]] && continue
        local file_field
        file_field="$(echo "$line" | cut -f1)"
        if [[ "$file_field" == "$FILE_NAME" ]]; then
            found_line="$line"
            break
        fi
    done < "$LOG_PATH"

    if [[ -z "$found_line" ]]; then
        echo "--- FAILED ---"
        echo "$FILE_NAME|未在操作日志中找到该文件"
        echo "=== END ==="
        return
    fi

    IFS=$'\t' read -r file orig_path dest_path folder method status <<< "$found_line"

    echo "--- RESTORED ---"
    if [[ ! -e "$dest_path" ]]; then
        echo "FAILED|$file|目标文件不存在: $dest_path"
        echo "=== END ==="
        return
    fi

    if [[ -e "$orig_path" ]]; then
        echo "FAILED|$file|原位置已有同名文件: $orig_path"
        echo "=== END ==="
        return
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        local parent_dir
        parent_dir="$(dirname "$orig_path")"
        mkdir -p "$parent_dir"
        mv "$dest_path" "$orig_path"
    fi

    echo "OK|$file|$dest_path|$orig_path"

    # Check if folder became empty and was auto-created
    echo ""
    echo "--- CLEANED FOLDERS ---"
    local dest_folder
    dest_folder="$(dirname "$dest_path")"

    while IFS= read -r cline; do
        [[ "$cline" == \#CREATED_FOLDER* ]] || continue
        IFS=$'\t' read -r _tag folder_name folder_path _created_at <<< "$cline"

        # Normalize paths for comparison (remove trailing slashes)
        local norm_fp="${folder_path%/}"
        local norm_df="${dest_folder%/}"

        if [[ "$norm_fp" == "$norm_df" ]]; then
            try_clean_folder "$folder_path" "$folder_name"
            break
        fi
    done < "$LOG_PATH"

    echo ""
    echo "=== END ==="
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

case "$COMMAND" in
    list-logs)
        do_list_logs ;;
    rollback-all)
        do_rollback_all ;;
    rollback-single)
        do_rollback_single ;;
    *)
        echo "Unknown command: $COMMAND"
        usage ;;
esac
