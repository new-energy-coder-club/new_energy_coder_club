# ============================================================
#  KIMI Code Dashboard - skill entry script
#  Defines Show-AIDashboard. Auto-runs only when invoked directly
#  (i.e., `pwsh dashboard.ps1`); when dot-sourced from a profile
#  it just registers the function.
# ============================================================

function Show-AIDashboard {
    [CmdletBinding()]
    param(
        [int]$RecentSkillsCount = 16,
        [int]$RecentProjectsCount = 6,
        [string[]]$ProjectRoots = @('D:\Project_env', 'D:\Dev_env', 'D:\Work_dev'),
        [string[]]$ExtraProjectPaths = @('D:\NEC-Claw')
    )

    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $date = Get-Date -Format 'yyyy/MM/dd HH:mm'

    # ── helper: validate project path ─────────────────────────
    function Test-IsValidProjectPath($path, [switch]$Strict) {
        if (-not $path) { return $false }
        if (-not (Test-Path $path -PathType Container)) { return $false }
        try { $fullPath = (Resolve-Path $path).Path } catch { return $false }
        $name = Split-Path $fullPath -Leaf

        # 排除根目录
        if ($fullPath -match '^[A-Z]:\\$') { return $false }

        # 排除系统目录与用户根目录
        $systemDirs = @('C:\Windows', 'C:\WINDOWS', 'C:\Program Files', 'C:\Program Files (x86)', 'C:\Users\29711')
        foreach ($sd in $systemDirs) {
            if ($fullPath -ieq $sd) { return $false }
        }

        # 排除通用非项目目录名
        $genericNames = @('Downloads', 'Desktop', 'Documents', 'temp', 'tmp', 'docs', 'workspace', 'init', 'release-new', 'release', 'dist', 'build')
        if ($genericNames -contains $name) { return $false }

        # 严格模式：再排除父容器目录与微信缓存等路径
        if ($Strict) {
            $containerNames = @('Project_env', 'Dev_env', 'Work_dev', 'Paper_env')
            if ($containerNames -contains $name) { return $false }
            if ($fullPath -match 'xwechat_files') { return $false }
            if ($fullPath -match 'system32') { return $false }
        }

        return $true
    }

    # ── header ────────────────────────────────────────────────
    Write-Host ''
    Write-Host '  ╔══════════════════════════════════════════════════╗' -ForegroundColor Cyan
    Write-Host "  ║       KIMI Code Dashboard  ·  $date        ║" -ForegroundColor White
    Write-Host '  ╚══════════════════════════════════════════════════╝' -ForegroundColor Cyan
    Write-Host ''

    # ── AI CLIs ──────────────────────────────────────────────
    Write-Host '  [ AI CLIs ]' -ForegroundColor Cyan
    $ais = @(
        @{ cmd = 'kimi';   label = 'Kimi CLI (Moonshot)'     },
        @{ cmd = 'claude'; label = 'Claude Code (Anthropic)' },
        @{ cmd = 'gemini'; label = 'Gemini CLI (Google)'     }
    )
    foreach ($ai in $ais) {
        $found = Get-Command $ai.cmd -ErrorAction SilentlyContinue
        if ($found) {
            Write-Host "    ✓  $($ai.cmd.PadRight(10)) $($ai.label)" -ForegroundColor Green
        } else {
            Write-Host "    ✗  $($ai.cmd.PadRight(10)) $($ai.label)  [not found]" -ForegroundColor DarkGray
        }
    }
    Write-Host ''

    # ── Recent Skills ─────────────────────────────────────────
    Write-Host '  [ Recent Skills ]' -ForegroundColor Cyan
    $skillRoots = @(
        "$env:USERPROFILE\.config\agents\skills",
        "$env:USERPROFILE\.kimi\skills"
    )
    $skillItems = @()
    foreach ($sr in $skillRoots) {
        if (Test-Path $sr) {
            $skillItems += Get-ChildItem $sr -Directory -ErrorAction SilentlyContinue | Select-Object Name, LastWriteTime, FullName
        }
    }
    if ($skillItems.Count -eq 0) {
        Write-Host '    (no skills found)' -ForegroundColor DarkGray
    } else {
        $now = Get-Date
        $top = $skillItems | Sort-Object LastWriteTime -Descending | Select-Object -First $RecentSkillsCount
        foreach ($e in $top) {
            $delta = $now - $e.LastWriteTime
            $rel = if     ($delta.TotalMinutes -lt 60) { '{0}m ago' -f [int]$delta.TotalMinutes }
                   elseif ($delta.TotalHours   -lt 24) { '{0}h ago' -f [int]$delta.TotalHours }
                   elseif ($delta.TotalDays    -lt 30) { '{0}d ago' -f [int]$delta.TotalDays }
                   else                                { $e.LastWriteTime.ToString('MM-dd') }
            Write-Host ("    ·  {0}  {1}" -f $e.Name.PadRight(32), $rel) -ForegroundColor White
        }
    }
    Write-Host ''

    # ── Recent Projects (from kimi.json work_dirs) ────────────
    Write-Host '  [ Recent Projects ]' -ForegroundColor Cyan
    $kimiJson = "$env:USERPROFILE\.kimi\kimi.json"
    $projectList = [System.Collections.Generic.List[PSObject]]::new()

    if (Test-Path $kimiJson) {
        try {
            $kj = Get-Content $kimiJson -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($kj.work_dirs) {
                $seen = @{}
                foreach ($wd in $kj.work_dirs) {
                    $p = $wd.path
                    if (-not (Test-IsValidProjectPath $p -Strict)) { continue }
                    if ($seen.ContainsKey($p)) { continue }
                    $seen[$p] = $true

                    $item = Get-Item $p -ErrorAction SilentlyContinue
                    if (-not $item) { continue }

                    $projectList.Add([PSCustomObject]@{
                        Path       = $p
                        Name       = $item.Name
                        LastWrite  = $item.LastWriteTime
                        IsActive   = [bool]$wd.last_session_id
                    })
                }
            }
        } catch {}
    }

    # Fallback: scan filesystem if kimi.json yields too few
    if ($projectList.Count -lt $RecentProjectsCount) {
        $fsProjects = @()
        foreach ($ep in $ExtraProjectPaths) {
            if (Test-Path $ep) { $fsProjects += Get-Item $ep }
        }
        foreach ($root in $ProjectRoots) {
            if (Test-Path $root) {
                $fsProjects += Get-ChildItem $root -Directory -ErrorAction SilentlyContinue
            }
        }
        $existingNames = $projectList | ForEach-Object { $_.Name }
        foreach ($fp in ($fsProjects | Sort-Object LastWriteTime -Descending)) {
            if ($fp.Name -in $existingNames) { continue }
            if (-not (Test-IsValidProjectPath $fp.FullName -Strict)) { continue }
            $projectList.Add([PSCustomObject]@{
                Path      = $fp.FullName
                Name      = $fp.Name
                LastWrite = $fp.LastWriteTime
                IsActive  = $false
            })
        }
    }

    $recent = $projectList |
        Sort-Object @{ Expression = { if ($_.IsActive) { 0 } else { 1 } }; Ascending = $true }, @{ Expression = { $_.LastWrite }; Descending = $true } |
        Select-Object -First $RecentProjectsCount

    if ($recent.Count -eq 0) {
        Write-Host '    (no projects found)' -ForegroundColor DarkGray
    } else {
        foreach ($p in $recent) {
            $age = $p.LastWrite.ToString('MM-dd')
            $badge = if ($p.IsActive) { '[active] ' } else { '         ' }
            $badgeColor = if ($p.IsActive) { 'Green' } else { 'White' }
            $name = $p.Name.PadRight(28)
            $shortPath = if ($p.Path.Length -gt 45) { '...' + $p.Path.Substring($p.Path.Length - 42) } else { $p.Path }
            Write-Host "    " -NoNewline
            Write-Host $badge -NoNewline -ForegroundColor $badgeColor
            Write-Host "$age  $name  " -NoNewline -ForegroundColor Gray
            Write-Host $shortPath -ForegroundColor DarkGray
        }
    }

    Write-Host ''
    Write-Host "  Type 'kimi' to start · '/skills' to browse · 'dev' to refresh" -ForegroundColor Gray
    Write-Host ''
}

# Auto-run only when this file is invoked directly (not dot-sourced).
if ($MyInvocation.InvocationName -ne '.') {
    Show-AIDashboard @args
}
