---
name: wechat-cli-export
description: Export WeChat group member lists via wechat-cli with automatic Windows encoding fixes. Use when the user needs to extract微信群成员列表, export wechat group contacts, read wechat chatroom members, or convert wechat-cli JSON output to CSV. Handles emoji and GBK encoding issues on Windows automatically.
---

# WeChat CLI Export

Export WeChat group member lists to CSV/JSON using `wechat-cli`, with automatic fixes for Windows GBK encoding issues (emoji crashes).

## Prerequisites

- `wechat-cli` must be installed and initialized (`wechat-cli init`)
- Python 3.10+

## Usage

### Quick Export (Single Group)

```bash
python scripts/export_members.py "群名称"
```

Example:
```bash
python scripts/export_members.py "26常工院NEC-RC主赛"
```

Outputs:
- `~/群成员_26常工院NEC-RC主赛.csv` — 三字段表格
- `~/members_26常工院NEC-RC主赛.json` — 完整原始数据

### Options

| Flag | Description |
|------|-------------|
| `-o DIR` | Custom output directory |
| `--csv-only` | Export CSV only |
| `--json-only` | Export JSON only |

```bash
python scripts/export_members.py "合规运营" -o D:\exports --csv-only
```

### Direct wechat-cli Usage

If the bundled script is insufficient, call `wechat-cli` directly with encoding fixes:

```powershell
$env:PYTHONIOENCODING = "utf-8"
wechat-cli members "群名称"
```

**Always set `PYTHONIOENCODING=utf-8` before running wechat-cli on Windows** to prevent emoji-related GBK crashes.

## Output Fields (CSV)

| Column | JSON Key | Description |
|--------|----------|-------------|
| 群昵称 | `nick_name` | Member's display name in the group |
| 备注 | `remark` | Your private remark for this contact |
| 微信号 | `username` | Internal wxid (e.g. `wxid_xxxxxxxx`) |

## Windows Encoding Fix

The bundled script automatically:
1. Sets `PYTHONIOENCODING=utf-8` for the subprocess
2. Falls back to GBK decoding if UTF-8 fails
3. Outputs CSV with UTF-8-BOM for Excel compatibility

If running `wechat-cli` manually on Windows and seeing `UnicodeEncodeError: 'gbk' codec can't encode character`, apply the fix in `wechat_cli/output/formatter.py`:

```python
# In output_json(), before json.dump():
if hasattr(file, 'reconfigure') and getattr(file, 'encoding', 'utf-8').lower() not in ('utf-8', 'utf8'):
    file.reconfigure(encoding='utf-8')
```
