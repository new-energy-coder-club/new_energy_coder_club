#!/usr/bin/env bash
# ==========================================================================
# organize-mac.sh — macOS 文件整理脚本（纯 Bash，零依赖）
# ==========================================================================
# 零删除/零覆盖策略。
# 权限前置校验、超大文件过滤、智能扫描。
# 生成 TSV 操作日志供回撤使用，stdout 输出结构化文本供 AI 分析。
# ==========================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SHORTCUT_EXTENSIONS="lnk app url webloc desktop"
SYSTEM_SKIP_NAMES="desktop.ini .DS_Store .localized Thumbs.db .com.apple.timemachine.donotpresent"

# Category map: extension -> category
# We build this as a function for lookup
get_category() {
    local ext="$1"
    case "$ext" in
        png|jpg|jpeg|gif|bmp|tiff|webp|svg|ico|heic|heif) echo "图片" ;;
        docx|pdf|txt|doc|ppt|pptx|odt|rtf|pages) echo "文档" ;;
        xlsx|csv|xls|numbers|ods|tsv) echo "表格" ;;
        exe|dmg|pkg|msi|apk|deb|rpm|appimage) echo "安装包" ;;
        mp3|wav|flac|m4a|ogg|aac|wma|aiff) echo "音频" ;;
        mp4|avi|mov|mkv|flv|wmv|webm|m4v|ts) echo "视频" ;;
        zip|rar|7z|tar|gz|bz2|xz|tgz) echo "压缩包" ;;
        log) echo "日志" ;;
        py|js|jsx|tsx|java|c|cpp|h|hpp|cs|go|rb|php|swift|kt|rs|lua|sh|bat|ps1|html|css|scss|less|json|xml|yaml|yml|sql|r|md|ini|cfg|conf|toml) echo "代码" ;;
        ttf|otf|woff|woff2|eot) echo "字体" ;;
        epub|mobi|azw3|djvu) echo "电子书" ;;
        psd|ai|sketch|fig|xd|indd) echo "设计文件" ;;
        *) echo "其他文件" ;;
    esac
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

usage() {
    echo "Usage: $0 <TARGET_DIR> [--phase phase1|phase2|all] [--size-threshold <GB>] [--whitelist file1,file2,...] [--dry-run]"
    exit 1
}

TARGET_DIR=""
PHASE="all"
SIZE_THRESHOLD="1"
WHITELIST=""
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --phase)
            PHASE="$2"; shift 2 ;;
        --size-threshold)
            SIZE_THRESHOLD="$2"; shift 2 ;;
        --whitelist)
            WHITELIST="$2"; shift 2 ;;
        --dry-run)
            DRY_RUN="true"; shift ;;
        -*)
            echo "Unknown option: $1"; usage ;;
        *)
            if [[ -z "$TARGET_DIR" ]]; then
                TARGET_DIR="$1"; shift
            else
                echo "Unexpected argument: $1"; usage
            fi
            ;;
    esac
done

if [[ -z "$TARGET_DIR" ]]; then
    usage
fi

# Resolve target directory
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
    echo '{"error":"Target directory does not exist: '"$TARGET_DIR"'"}'
    exit 1
}

if [[ ! -d "$TARGET_DIR" ]]; then
    echo '{"error":"Target directory does not exist: '"$TARGET_DIR"'"}'
    exit 1
fi

# Parse whitelist into an array
IFS=',' read -ra WHITELIST_ARR <<< "$WHITELIST"

# ---------------------------------------------------------------------------
# Log setup — TSV format for disk, structured text for stdout
# ---------------------------------------------------------------------------

LOG_DIR="$TARGET_DIR/.file_organizer_logs"
TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
TIMESTAMP_ISO="$(date '+%Y-%m-%dT%H:%M:%S')"
LOG_FILE="$LOG_DIR/organize_${TIMESTAMP}.log"

# Counters
TOTAL_SCANNED=0
AUTO_ORGANIZED=0
SKIPPED_COUNT=0
ERROR_COUNT=0

# Accumulate output data in temp files
TMPDIR_WORK="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_WORK"' EXIT

OPERATIONS_FILE="$TMPDIR_WORK/operations.tsv"
SKIPPED_FILE="$TMPDIR_WORK/skipped.tsv"
ERRORS_FILE="$TMPDIR_WORK/errors.tsv"
CREATED_FOLDERS_FILE="$TMPDIR_WORK/created_folders.tsv"
UNMATCHED_FILE="$TMPDIR_WORK/unmatched.tsv"

touch "$OPERATIONS_FILE" "$SKIPPED_FILE" "$ERRORS_FILE" "$CREATED_FOLDERS_FILE" "$UNMATCHED_FILE"

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

# Check if a value is in a space-separated list
in_list() {
    local val="$1" list="$2"
    for item in $list; do
        [[ "$item" == "$val" ]] && return 0
    done
    return 1
}

# Check if a value is in the whitelist array
in_whitelist() {
    local val="$1"
    for item in "${WHITELIST_ARR[@]}"; do
        [[ "$item" == "$val" ]] && return 0
    done
    return 1
}

# Get file extension (lowercase, without dot)
get_ext() {
    local name="$1"
    if [[ "$name" == *.* ]]; then
        local ext="${name##*.}"
        echo "$ext" | tr '[:upper:]' '[:lower:]'  # lowercase (macOS compatible)
    else
        echo ""
    fi
}

# Get file stem (name without extension)
get_stem() {
    local name="$1"
    if [[ "$name" == *.* ]]; then
        echo "${name%.*}"
    else
        echo "$name"
    fi
}

# Get file size in bytes (macOS compatible)
get_file_size() {
    stat -f%z "$1" 2>/dev/null || echo "0"
}

# Get file access time as Unix timestamp (macOS compatible)
get_atime() {
    stat -f%a "$1" 2>/dev/null || echo "0"
}

# Get file modification time as Unix timestamp (macOS compatible)
get_mtime() {
    stat -f%m "$1" 2>/dev/null || echo "0"
}

# Convert bytes to GB (integer comparison, returns 1 if > threshold)
exceeds_size_threshold() {
    local size_bytes="$1"
    local threshold_gb="$2"
    # threshold_gb can be decimal like 1.5, convert to bytes
    # Use awk for floating point
    awk -v size="$size_bytes" -v thresh="$threshold_gb" 'BEGIN { if (size > thresh * 1073741824) exit 0; else exit 1 }'
}

# Format bytes to human-readable GB
format_size_gb() {
    local size_bytes="$1"
    awk -v size="$size_bytes" 'BEGIN { printf "%.2f", size / 1073741824 }'
}

# Check if file is a shortcut/alias
is_shortcut() {
    local filepath="$1"
    local ext
    ext="$(get_ext "$(basename "$filepath")")"

    # Check extension
    if in_list "$ext" "$SHORTCUT_EXTENSIONS"; then
        return 0
    fi

    # macOS alias detection
    if [[ "$(uname)" == "Darwin" ]]; then
        local kind
        kind="$(mdls -name kMDItemKind "$filepath" 2>/dev/null || echo "")"
        if [[ "$kind" == *"Alias"* ]]; then
            return 0
        fi
    fi

    return 1
}

# Check if file is a system file
is_system_file() {
    local name="$1"
    # Check name in system skip list
    if in_list "$name" "$SYSTEM_SKIP_NAMES"; then
        return 0
    fi
    # Check if hidden file (starts with .)
    if [[ "$name" == .* ]]; then
        return 0
    fi
    return 1
}

# Check if file is locked/in use
is_file_locked() {
    local filepath="$1"
    if command -v lsof &>/dev/null; then
        if lsof "$filepath" &>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Safe move: move file to destination, handle name conflicts
# Outputs the actual destination path
safe_move() {
    local src="$1"
    local dst_dir="$2"
    local filename
    filename="$(basename "$src")"
    local stem
    stem="$(get_stem "$filename")"
    local ext
    ext="$(get_ext "$filename")"

    # Create destination directory if needed
    if [[ "$DRY_RUN" == "false" ]]; then
        mkdir -p "$dst_dir"
    fi

    local dst="$dst_dir/$filename"

    # Handle name conflicts
    if [[ -e "$dst" ]]; then
        local counter=1
        while [[ -e "$dst" ]]; do
            if [[ -n "$ext" ]]; then
                dst="$dst_dir/${stem}_${counter}.${ext}"
            else
                dst="$dst_dir/${stem}_${counter}"
            fi
            counter=$((counter + 1))
        done
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        mv "$src" "$dst"
    fi

    echo "$dst"
}

# Record a created folder (if not already recorded)
record_created_folder() {
    local folder_name="$1"
    local folder_path="$2"
    # Check if already recorded
    if ! grep -q "^${folder_name}	" "$CREATED_FOLDERS_FILE" 2>/dev/null; then
        printf '%s\t%s\t%s\n' "$folder_name" "$folder_path" "$TIMESTAMP_ISO" >> "$CREATED_FOLDERS_FILE"
    fi
}

# ---------------------------------------------------------------------------
# Keyword match: check if file stem contains folder name
# ---------------------------------------------------------------------------
keyword_match_folder() {
    local file_stem="$1"
    local folder_name="$2"

    # Folder name must be >= 2 chars
    if [[ ${#folder_name} -lt 2 ]]; then
        return 1
    fi

    # Case-insensitive contains check (macOS compatible)
    local fs_lower=$(echo "$file_stem" | tr '[:upper:]' '[:lower:]')
    local fn_lower=$(echo "$folder_name" | tr '[:upper:]' '[:lower:]')
    if [[ "$fs_lower" == *"$fn_lower"* ]]; then
        return 0
    fi
    return 1
}

# ---------------------------------------------------------------------------
# Naming pattern match: check if file stem shares common prefix with
# existing files in a folder (>= 3 chars prefix, >= 2 matches)
# ---------------------------------------------------------------------------
naming_pattern_match() {
    local file_stem="$1"
    local folder_path="$2"
    local match_count=0

    # Get stems of files in the folder
    for entry in "$folder_path"/*; do
        [[ -f "$entry" ]] || continue
        local existing_name
        existing_name="$(basename "$entry")"
        local existing_stem
        existing_stem="$(get_stem "$existing_name")"

        # Calculate common prefix length
        local common_len=0
        local min_len=${#file_stem}
        [[ ${#existing_stem} -lt $min_len ]] && min_len=${#existing_stem}

        local i=0
        while [[ $i -lt $min_len ]]; do
            # Use cut for character extraction (macOS compatible)
            local fs_char=$(echo "$file_stem" | cut -c$((i+1)))
            local es_char=$(echo "$existing_stem" | cut -c$((i+1)))
            if [[ "$fs_char" == "$es_char" ]]; then
                common_len=$((common_len + 1))
            else
                break
            fi
            i=$((i + 1))
        done

        if [[ $common_len -ge 3 ]]; then
            match_count=$((match_count + 1))
        fi

        # Early exit if we already have enough matches
        if [[ $match_count -ge 2 ]]; then
            return 0
        fi
    done

    return 1
}

# ---------------------------------------------------------------------------
# Core: Scan candidate files
# ---------------------------------------------------------------------------
scan_candidates() {
    local target="$1"

    for entry in "$target"/*; do
        # Skip if no files (glob didn't match)
        [[ -e "$entry" ]] || continue
        # Skip directories
        [[ -d "$entry" ]] && continue

        local name
        name="$(basename "$entry")"

        # Whitelist check
        if [[ ${#WHITELIST_ARR[@]} -gt 0 ]] && in_whitelist "$name"; then
            printf '%s\t%s\t%s\n' "$name" "$entry" "用户白名单豁免" >> "$SKIPPED_FILE"
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            continue
        fi

        # Shortcut check
        if is_shortcut "$entry"; then
            printf '%s\t%s\t%s\n' "$name" "$entry" "快捷方式/别名，禁止移动" >> "$SKIPPED_FILE"
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            continue
        fi

        # System file check
        if is_system_file "$name"; then
            printf '%s\t%s\t%s\n' "$name" "$entry" "系统文件，自动跳过" >> "$SKIPPED_FILE"
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            continue
        fi

        # Permission check
        if [[ ! -r "$entry" ]] || [[ ! -w "$entry" ]]; then
            printf '%s\t%s\t%s\t%s\n' "$name" "$entry" "无读写权限" "请检查文件权限后重试" >> "$ERRORS_FILE"
            ERROR_COUNT=$((ERROR_COUNT + 1))
            continue
        fi

        # Size check
        local size_bytes
        size_bytes="$(get_file_size "$entry")"
        if exceeds_size_threshold "$size_bytes" "$SIZE_THRESHOLD"; then
            local size_gb
            size_gb="$(format_size_gb "$size_bytes")"
            printf '%s\t%s\t%s\t%s\n' "$name" "$entry" "文件大小 ${size_gb} GB（超过 ${SIZE_THRESHOLD} GB 阈值）" "建议手动移入对应分类文件夹" >> "$ERRORS_FILE"
            ERROR_COUNT=$((ERROR_COUNT + 1))
            continue
        fi

        # File locked check
        if is_file_locked "$entry"; then
            printf '%s\t%s\t%s\t%s\n' "$name" "$entry" "文件被占用，无法移动" "关闭占用该文件的程序后重试" >> "$ERRORS_FILE"
            ERROR_COUNT=$((ERROR_COUNT + 1))
            continue
        fi

        # Passed all checks — add to candidates
        local ext stem atime mtime
        ext="$(get_ext "$name")"
        stem="$(get_stem "$name")"
        atime="$(get_atime "$entry")"
        mtime="$(get_mtime "$entry")"

        # Output candidate: name<TAB>path<TAB>stem<TAB>ext<TAB>size<TAB>atime<TAB>mtime
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$entry" "$stem" "$ext" "$size_bytes" "$atime" "$mtime"
        TOTAL_SCANNED=$((TOTAL_SCANNED + 1))
    done
}

# ---------------------------------------------------------------------------
# Core: Match candidates to existing folders (Priority 1)
# ---------------------------------------------------------------------------
match_existing_folders() {
    local target="$1"
    local candidates_file="$2"
    local status_val="done"
    [[ "$DRY_RUN" == "true" ]] && status_val="dry_run"

    # Collect existing folders (use temporary files instead of associative array for macOS compatibility)
    local folders_tmp="$TMPDIR_WORK/folders_list"
    local folders_map="$TMPDIR_WORK/folders_map"

    for d in "$target"/*/; do
        [[ -d "$d" ]] || continue
        local dname
        dname="$(basename "$d")"
        # Skip hidden folders
        [[ "$dname" == .* ]] && continue
        echo "$dname" >> "$folders_tmp"
        echo "$dname|$d" >> "$folders_map"
    done

    # Process each candidate
    while IFS=$'\t' read -r name filepath stem ext size_bytes atime mtime; do
        local matched="false"

        # Keyword match
        while IFS='|' read -r folder_name folder_path; do
            if keyword_match_folder "$stem" "$folder_name"; then
                local dst
                dst="$(safe_move "$filepath" "$folder_path")"
                printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$filepath" "$dst" "$folder_name" "关键词匹配已有文件夹" "$status_val" >> "$OPERATIONS_FILE"
                AUTO_ORGANIZED=$((AUTO_ORGANIZED + 1))
                matched="true"
                break
            fi
        done < "$folders_map"
        [[ "$matched" == "true" ]] && continue

        # Naming pattern match
        while IFS='|' read -r folder_name folder_path; do
            if naming_pattern_match "$stem" "$folder_path"; then
                local dst
                dst="$(safe_move "$filepath" "$folder_path")"
                printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$filepath" "$dst" "$folder_name" "命名规律匹配已有文件夹" "$status_val" >> "$OPERATIONS_FILE"
                AUTO_ORGANIZED=$((AUTO_ORGANIZED + 1))
                matched="true"
                break
            fi
        done < "$folders_map"
        [[ "$matched" == "true" ]] && continue

        # Unmatched — pass through
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$filepath" "$stem" "$ext" "$size_bytes" "$atime" "$mtime" >> "$UNMATCHED_FILE"
    done < "$candidates_file"
}

# ---------------------------------------------------------------------------
# Core: Fallback classification (Priority 2 & 3)
# ---------------------------------------------------------------------------
fallback_classify() {
    local target="$1"
    local unmatched_file="$2"
    local status_val="done"
    [[ "$DRY_RUN" == "true" ]] && status_val="dry_run"

    local now
    now="$(date +%s)"
    local sixty_days=$((60 * 86400))

    # Separate infrequent and remaining files
    local infrequent_file="$TMPDIR_WORK/infrequent.tsv"
    local remaining_file="$TMPDIR_WORK/remaining.tsv"
    touch "$infrequent_file" "$remaining_file"

    while IFS=$'\t' read -r name filepath stem ext size_bytes atime mtime; do
        if [[ $((now - atime)) -gt $sixty_days ]]; then
            printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$filepath" "$stem" "$ext" "$size_bytes" "$atime" "$mtime" >> "$infrequent_file"
        else
            printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$filepath" "$stem" "$ext" "$size_bytes" "$atime" "$mtime" >> "$remaining_file"
        fi
    done < "$unmatched_file"

    local infrequent_count
    infrequent_count="$(wc -l < "$infrequent_file" | tr -d ' ')"

    # Priority 2: Infrequent files (>= 2 files, > 60 days since last access)
    if [[ "$infrequent_count" -ge 2 ]]; then
        local folder_name="不常用文件"
        local dest_folder="$target/$folder_name"
        if [[ ! -d "$dest_folder" ]]; then
            record_created_folder "$folder_name" "$dest_folder"
        fi
        while IFS=$'\t' read -r name filepath stem ext size_bytes atime mtime; do
            local dst
            dst="$(safe_move "$filepath" "$dest_folder")"
            printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$filepath" "$dst" "$folder_name" "不常用文件归类（超过60天未使用）" "$status_val" >> "$OPERATIONS_FILE"
            AUTO_ORGANIZED=$((AUTO_ORGANIZED + 1))
        done < "$infrequent_file"
    else
        # Less than 2 infrequent files, add them to remaining
        cat "$infrequent_file" >> "$remaining_file"
    fi

    # Priority 3: Classify by file type
    while IFS=$'\t' read -r name filepath stem ext size_bytes atime mtime; do
        local folder_name
        folder_name="$(get_category "$ext")"
        local dest_folder="$target/$folder_name"
        if [[ ! -d "$dest_folder" ]]; then
            record_created_folder "$folder_name" "$dest_folder"
        fi
        local dst
        dst="$(safe_move "$filepath" "$dest_folder")"
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$filepath" "$dst" "$folder_name" "按文件类型分类" "$status_val" >> "$OPERATIONS_FILE"
        AUTO_ORGANIZED=$((AUTO_ORGANIZED + 1))
    done < "$remaining_file"
}

# ---------------------------------------------------------------------------
# Save log to disk (TSV format)
# ---------------------------------------------------------------------------
save_log() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return
    fi

    mkdir -p "$LOG_DIR"

    {
        # Header line (metadata)
        printf '#META\ttimestamp=%s\ttarget_dir=%s\tphase=%s\tsize_threshold_gb=%s\tdry_run=%s\n' \
            "$TIMESTAMP_ISO" "$TARGET_DIR" "$PHASE" "$SIZE_THRESHOLD" "$DRY_RUN"

        # Created folders
        while IFS=$'\t' read -r folder_name folder_path created_at; do
            printf '#CREATED_FOLDER\t%s\t%s\t%s\n' "$folder_name" "$folder_path" "$created_at"
        done < "$CREATED_FOLDERS_FILE"

        # Operations: file<TAB>original_path<TAB>destination_path<TAB>folder<TAB>method<TAB>status
        while IFS=$'\t' read -r file orig dest folder method status; do
            printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$file" "$orig" "$dest" "$folder" "$method" "$status"
        done < "$OPERATIONS_FILE"

        # Skipped files
        while IFS=$'\t' read -r file path reason; do
            printf '#SKIPPED\t%s\t%s\t%s\n' "$file" "$path" "$reason"
        done < "$SKIPPED_FILE"

        # Errors
        while IFS=$'\t' read -r file path reason suggestion; do
            printf '#ERROR\t%s\t%s\t%s\t%s\n' "$file" "$path" "$reason" "$suggestion"
        done < "$ERRORS_FILE"

        # Summary
        printf '#SUMMARY\ttotal=%d\torganized=%d\tskipped=%d\terrors=%d\tcreated_folders=%d\n' \
            "$TOTAL_SCANNED" "$AUTO_ORGANIZED" "$SKIPPED_COUNT" "$ERROR_COUNT" \
            "$(wc -l < "$CREATED_FOLDERS_FILE" | tr -d ' ')"
    } > "$LOG_FILE"
}

# ---------------------------------------------------------------------------
# Output structured text to stdout (for AI to parse)
# ---------------------------------------------------------------------------
output_results() {
    echo "=== FILE ORGANIZER RESULTS ==="
    echo "timestamp: $TIMESTAMP_ISO"
    echo "target_dir: $TARGET_DIR"
    echo "phase: $PHASE"
    echo "dry_run: $DRY_RUN"
    echo "log_file: $LOG_FILE"
    echo ""

    echo "--- SUMMARY ---"
    echo "total_scanned: $TOTAL_SCANNED"
    echo "auto_organized: $AUTO_ORGANIZED"
    echo "skipped_count: $SKIPPED_COUNT"
    echo "error_count: $ERROR_COUNT"
    echo "created_folder_count: $(wc -l < "$CREATED_FOLDERS_FILE" | tr -d ' ')"
    echo ""

    # Operations
    local op_count
    op_count="$(wc -l < "$OPERATIONS_FILE" | tr -d ' ')"
    if [[ "$op_count" -gt 0 ]]; then
        echo "--- OPERATIONS ($op_count) ---"
        echo "file|original_path|destination_path|destination_folder|method|status"
        while IFS=$'\t' read -r file orig dest folder method status; do
            echo "$file|$orig|$dest|$folder|$method|$status"
        done < "$OPERATIONS_FILE"
        echo ""
    fi

    # Created folders
    local cf_count
    cf_count="$(wc -l < "$CREATED_FOLDERS_FILE" | tr -d ' ')"
    if [[ "$cf_count" -gt 0 ]]; then
        echo "--- CREATED FOLDERS ($cf_count) ---"
        while IFS=$'\t' read -r folder_name folder_path created_at; do
            echo "$folder_name|$folder_path"
        done < "$CREATED_FOLDERS_FILE"
        echo ""
    fi

    # Unmatched files (only for phase1)
    if [[ "$PHASE" == "phase1" ]]; then
        local um_count
        um_count="$(wc -l < "$UNMATCHED_FILE" | tr -d ' ')"
        if [[ "$um_count" -gt 0 ]]; then
            echo "--- UNMATCHED FILES ($um_count) ---"
            echo "file|path|ext|size|atime|mtime"
            while IFS=$'\t' read -r name filepath stem ext size_bytes atime mtime; do
                echo "$name|$filepath|$ext|$size_bytes|$atime|$mtime"
            done < "$UNMATCHED_FILE"
            echo ""
        fi

        # Existing folders
        echo "--- EXISTING FOLDERS ---"
        for d in "$TARGET_DIR"/*/; do
            [[ -d "$d" ]] || continue
            local dname
            dname="$(basename "$d")"
            [[ "$dname" == .* ]] && continue
            echo "$dname"
        done
        echo ""
    fi

    # Skipped
    if [[ "$SKIPPED_COUNT" -gt 0 ]]; then
        echo "--- SKIPPED ($SKIPPED_COUNT) ---"
        echo "file|path|reason"
        while IFS=$'\t' read -r file path reason; do
            echo "$file|$path|$reason"
        done < "$SKIPPED_FILE"
        echo ""
    fi

    # Errors
    if [[ "$ERROR_COUNT" -gt 0 ]]; then
        echo "--- ERRORS ($ERROR_COUNT) ---"
        echo "file|path|reason|suggestion"
        while IFS=$'\t' read -r file path reason suggestion; do
            echo "$file|$path|$reason|$suggestion"
        done < "$ERRORS_FILE"
        echo ""
    fi

    echo "=== END ==="
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

CANDIDATES_FILE="$TMPDIR_WORK/candidates.tsv"

if [[ "$PHASE" == "phase2" ]]; then
    # Phase 2: Fallback classification for remaining files
    scan_candidates "$TARGET_DIR" > "$CANDIDATES_FILE"
    # In phase2, all candidates go to fallback directly
    cp "$CANDIDATES_FILE" "$UNMATCHED_FILE"
    TOTAL_SCANNED="$(wc -l < "$CANDIDATES_FILE" | tr -d ' ')"
    fallback_classify "$TARGET_DIR" "$UNMATCHED_FILE"
    save_log
    output_results
    exit 0
fi

# Phase 1 or all: scan + priority-1 matching
scan_candidates "$TARGET_DIR" > "$CANDIDATES_FILE"
TOTAL_SCANNED="$(wc -l < "$CANDIDATES_FILE" | tr -d ' ')"

match_existing_folders "$TARGET_DIR" "$CANDIDATES_FILE"

if [[ "$PHASE" == "phase1" ]]; then
    # Output unmatched for AI semantic analysis
    save_log
    output_results
    exit 0
fi

# Phase "all": continue with fallback
fallback_classify "$TARGET_DIR" "$UNMATCHED_FILE"
save_log
output_results
