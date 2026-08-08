---
name: ai-dev-dashboard
description: Prints the PowerShell AI Dev Dashboard — AI CLIs status, recently-used Skills across Kimi/Claude/AtomCode, and recent projects merged from Kimi Code, Claude Code, and AtomGit. Use when the user asks to "show dashboard", "run dev", "refresh dashboard", or to inspect recent Skill/project activity on the local machine.
---

# AI Dev Dashboard

A PowerShell-based startup dashboard for a local dev workstation. It reports:

- **AI CLIs** — presence check for `kimi`, `claude`, `gemini`, `atomcode` on PATH
- **Recent Skills** — top N Skills (default 5) across **Kimi Code**, **Claude Code**, **AtomCode**, and `~/.config/agents/skills`, merged by name (latest wins) with a source badge `[K C A G]`
- **Recent Projects** — top N projects (default 5) merged from three sources, deduped by absolute path, each tagged with which AI tools touched it

## How to invoke

Three equivalent ways:

1. **From PowerShell** (interactive, fastest): type `dev` or `dash`. Aliases are registered by the user's profile, which dot-sources `dashboard.ps1`.
2. **Standalone** (from any shell):
   ```powershell
   pwsh -NoProfile -File "$HOME\.claude\skills\ai-dev-dashboard\dashboard.ps1"
   ```
3. **As a function**, after dot-sourcing:
   ```powershell
   . "$HOME\.claude\skills\ai-dev-dashboard\dashboard.ps1"
   Show-AIDashboard -RecentSkillsCount 8 -RecentProjectsCount 6
   ```

## Parameters (Show-AIDashboard)

| Parameter               | Default                                       | Purpose                                  |
| ----------------------- | --------------------------------------------- | ---------------------------------------- |
| `-RecentSkillsCount`    | `5`                                           | Rows in `[Recent Skills]`                |
| `-RecentProjectsCount`  | `5`                                           | Rows in `[Recent Projects]`              |
| `-ProjectRoots`         | `D:\Project_env, D:\Dev_env, D:\Work_dev`     | Roots scanned for fallback project list  |
| `-ExtraProjectPaths`    | `D:\NEC-Claw`                                 | Individual paths added as-is             |

## Source badges

Each row is tagged with which tool's data store contributed the entry:

| Badge | Tool         | Skills scanned at                | Projects scanned at              |
| ----- | ------------ | -------------------------------- | -------------------------------- |
| `K`   | Kimi Code    | `~/.kimi/skills/`                | `~/.kimi/kimi.json → work_dirs`  |
| `C`   | Claude Code  | `~/.claude/skills/`              | `~/.claude/projects/<enc>/` (decoded from dir name) |
| `A`   | AtomGit      | `~/.atomcode/skills/`            | `~/.atomcode/recent_dirs.txt`    |
| `G`   | Generic      | `~/.config/agents/skills/`       | —                                |

A row like `[KCA]` means "this skill/project was recently used by Kimi, Claude, and AtomGit."

## Project merge algorithm

1. Read `~/.kimi/kimi.json` → `work_dirs[]`, mark `IsActive = (last_session_id != null)`
2. Scan `~/.claude/projects/`, decode dir names like `D--Project-env-SolarGlyph` → `D:\Project_env\SolarGlyph`, treat presence as `IsActive = true`, use dir `LastWriteTime`
3. Read `~/.atomcode/recent_dirs.txt` top-down; assign pseudo-mtime `(now - rank)` so the most-recent line wins the sort, force `IsActive = true`
4. Fallback to scanning `$ProjectRoots` + `$ExtraProjectPaths` if merged list < `-RecentProjectsCount`
5. Sort by `(IsActive desc, LastWrite desc)`, take top N

Skill merge: same name across multiple `Source` dirs is collapsed into one row, with the latest `LastWriteTime` and the source badges concatenated (`[KC]`).

## Filtering rules

`Test-IsValidProjectPath` rejects:
- Drive roots (`C:\`, `D:\`)
- System dirs (`C:\Windows`, `C:\Program Files`, `C:\Users\29711` itself)
- Generic folder names (`Downloads`, `Desktop`, `Documents`, `temp`, `docs`, `dist`, `build`, …)
- Container roots (`Project_env`, `Dev_env`, `Work_dev`, `Paper_env`) in `-Strict` mode
- WeChat cache paths (`xwechat_files`), `system32`

## Encoding

`dashboard.ps1` is saved as **UTF-8 with BOM** so Windows PowerShell 5.1 parses the box-drawing characters and `·` correctly. Do not strip the BOM — without it, PS 5.1 misreads the file as ANSI and the parse fails with `字符串缺少终止符`.

## Integration with PowerShell profile

```powershell
. "$HOME\.claude\skills\ai-dev-dashboard\dashboard.ps1"
Set-Alias dash Show-AIDashboard
Set-Alias dev  Show-AIDashboard
```

`dashboard.ps1` auto-runs itself when invoked directly (`pwsh dashboard.ps1`) but stays silent when dot-sourced — so the profile just imports the function without printing on every shell start.

## Performance

Skill scan is a `Get-ChildItem` over 4 small dirs (<100 entries total). Project scan reads one JSON, one text file, and one directory listing — all cheap. Total runtime is well under 1 s on a typical workstation.
