---
name: ai-dev-dashboard
description: Prints the PowerShell AI Dev Dashboard (AI CLIs status, recently called Skills with counts, recent Claude tasks, recent local projects). Use when the user asks to "show dashboard", "run dev", "refresh dashboard", or to inspect recent Skill usage stats on the local machine.
---

# AI Dev Dashboard

A PowerShell-based startup dashboard for a local dev workstation. It reports:

- **AI CLIs** — presence check for `claude`, `kimi`, `gemini` on PATH
- **Recent Skills** — top N Skills called in Claude Code, by most-recent invocation, with call counts. Parsed from `%USERPROFILE%\.claude\projects\*.jsonl` (only real `"name":"Skill"` tool_use entries are counted).
- **Recent Tasks** — most recent Claude task files from `%USERPROFILE%\.claude\tasks\`
- **Recent Projects** — newest project directories under configurable roots (`D:\Project_env`, `D:\Dev_env`, `D:\Work_dev`, plus `D:\NEC-Claw`)

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
   Show-AIDashboard -RecentSkillsCount 12
   ```

## Parameters (Show-AIDashboard)

| Parameter               | Default                                             | Purpose                        |
| ----------------------- | --------------------------------------------------- | ------------------------------ |
| `-RecentSkillsCount`    | `8`                                                 | Rows in [Recent Skills]        |
| `-RecentTasksCount`     | `6`                                                 | Rows in [Recent Tasks]         |
| `-RecentProjectsCount`  | `3`                                                 | Rows in [Recent Projects]      |
| `-ProjectRoots`         | `D:\Project_env, D:\Dev_env, D:\Work_dev`           | Roots scanned for subfolders   |
| `-ExtraProjectPaths`    | `D:\NEC-Claw`                                       | Individual paths added as-is   |

## Customization

Edit `dashboard.ps1` to:
- Add/remove AI CLIs — modify the `$ais` array in the `[AI CLIs]` section.
- Change column widths — adjust `.PadRight(...)` in the respective sections.
- Switch the banner title or colors — look for `AI Dev Dashboard` at the top.

## Integration with PowerShell profile

The profile (`$PROFILE`) should dot-source this script so the `dev` / `dash` aliases persist:

```powershell
. "$HOME\.claude\skills\ai-dev-dashboard\dashboard.ps1"
Set-Alias dash Show-AIDashboard
Set-Alias dev  Show-AIDashboard
```

`dashboard.ps1` auto-runs itself when invoked directly (`pwsh dashboard.ps1`) but stays silent when dot-sourced — so the profile just imports the function without printing on every shell start.

## Performance

Full parse across `~/.claude/projects/*.jsonl` is ~500 ms for ~20 MB of logs on a typical workstation. Stats are computed fresh on every call — no cache. If log volume grows large (>100 MB), consider adding a cache file keyed by `LastWriteTime` of the jsonl files.

## Data sources

| Section          | Source                                                |
| ---------------- | ----------------------------------------------------- |
| AI CLIs          | `Get-Command` on PATH                                 |
| Recent Skills    | `%USERPROFILE%\.claude\projects\*.jsonl` (regex scan) |
| Recent Tasks     | `%USERPROFILE%\.claude\tasks\*\*.json`                |
| Recent Projects  | Directories under `$ProjectRoots` + `$ExtraProjectPaths` |
