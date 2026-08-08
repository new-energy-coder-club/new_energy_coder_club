# ============================================================
#  KIMI Code Dashboard - skill entry script
#  Defines Show-AIDashboard. Auto-runs only when invoked directly
#  (i.e., `pwsh dashboard.ps1`); when dot-sourced from a profile
#  it just registers the function.
#
#  Data sources (top5 合并):
#    Skills   : ~/.kimi/skills, ~/.claude/skills, ~/.atomcode/skills,
#               ~/.config/agents/skills
#    Projects : ~/.kimi/kimi.json, ~/.claude/projects/,
#               ~/.atomcode/recent_dirs.txt
# ============================================================

function Show-AIDashboard {
    [CmdletBinding()]
    param(
        [int]$RecentSkillsCount = 5,
        [int]$RecentProjectsCount = 5,
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

    # ── helper: Claude 项目目录编码 ↔ 路径 ────────────────────
    #   "D--Project-env-SolarGlyph"  →  "D:\Project_env\SolarGlyph"
    function ConvertFrom-ClaudeProjectDir([string]$name) {
        if ($name -notmatch '^[A-Z]-') { return $null }
        $drive = $name.Substring(0, 1)
        $rest  = $name.Substring(2) -replace '-', '\'
        return "${drive}:\${rest}"
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
        @{ cmd = 'kimi';     label = 'Kimi CLI (Moonshot)'       },
        @{ cmd = 'claude';   label = 'Claude Code (Anthropic)'   },
        @{ cmd = 'gemini';   label = 'Gemini CLI (Google)'       },
        @{ cmd = 'atomcode'; label = 'AtomCode (AtomGit)'        }
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

    # ── Recent Skills (Kimi + Claude + AtomCode) ──────────────
    Write-Host '  [ Recent Skills ]' -ForegroundColor Cyan
    $skillSources = @(
        @{ root = "$env:USERPROFILE\.kimi\skills";             tag = 'K' },
        @{ root = "$env:USERPROFILE\.claude\skills";           tag = 'C' },
        @{ root = "$env:USERPROFILE\.atomcode\skills";         tag = 'A' },
        @{ root = "$env:USERPROFILE\.config\agents\skills";    tag = 'G' }
    )
    $skillItems = @()
    foreach ($ss in $skillSources) {
        if (Test-Path $ss.root) {
            Get-ChildItem $ss.root -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                $skillItems += [PSCustomObject]@{
                    Name         = $_.Name
                    LastWriteTime= $_.LastWriteTime
                    Source       = $ss.tag
                }
            }
        }
    }
    if ($skillItems.Count -eq 0) {
        Write-Host '    (no skills found)' -ForegroundColor DarkGray
    } else {
        $now = Get-Date
        # 同名 skill 跨工具合并（保留最新）
        $merged = $skillItems | Group-Object Name | ForEach-Object {
            $latest = $_.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $tags   = ($_.Group | Sort-Object Source -Unique | ForEach-Object Source) -join ''
            [PSCustomObject]@{
                Name          = $latest.Name
                LastWriteTime = $latest.LastWriteTime
                Source        = $tags
            }
        }
        $top = $merged | Sort-Object LastWriteTime -Descending | Select-Object -First $RecentSkillsCount
        foreach ($e in $top) {
            $delta = $now - $e.LastWriteTime
            $rel = if     ($delta.TotalMinutes -lt 60) { '{0}m ago' -f [int]$delta.TotalMinutes }
                   elseif ($delta.TotalHours   -lt 24) { '{0}h ago' -f [int]$delta.TotalHours }
                   elseif ($delta.TotalDays    -lt 30) { '{0}d ago' -f [int]$delta.TotalDays }
                   else                                { $e.LastWriteTime.ToString('MM-dd') }
            $tagBadge = "[{0}]" -f $e.Source
            Write-Host ("    ·  {0}  {1,-7} {2}" -f $e.Name.PadRight(32), $tagBadge, $rel) -ForegroundColor White
        }
    }
    Write-Host ''

    # ── Recent Projects (Kimi + Claude + AtomGit 合并) ────────
    Write-Host '  [ Recent Projects ]' -ForegroundColor Cyan
    $projectList = [System.Collections.Generic.List[PSObject]]::new()
    $seenPath = @{}   # path → index in $projectList (for merging)

    # 1) Kimi: ~/.kimi/kimi.json
    $kimiJson = "$env:USERPROFILE\.kimi\kimi.json"
    if (Test-Path $kimiJson) {
        try {
            $kj = Get-Content $kimiJson -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($kj.work_dirs) {
                foreach ($wd in $kj.work_dirs) {
                    $p = $wd.path
                    if (-not (Test-IsValidProjectPath $p -Strict)) { continue }
                    $item = Get-Item $p -ErrorAction SilentlyContinue
                    if (-not $item) { continue }
                    if (-not $seenPath.ContainsKey($p)) {
                        $seenPath[$p] = $projectList.Count
                        $projectList.Add([PSCustomObject]@{
                            Path       = $p
                            Name       = $item.Name
                            LastWrite  = $item.LastWriteTime
                            IsActive   = [bool]$wd.last_session_id
                            Source     = 'K'
                        })
                    }
                }
            }
        } catch {}
    }

    # 2) Claude: ~/.claude/projects/ (目录名编码 + mtime)
    $claudeRoot = "$env:USERPROFILE\.claude\projects"
    if (Test-Path $claudeRoot) {
        Get-ChildItem $claudeRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $realPath = ConvertFrom-ClaudeProjectDir $_.Name
            if (-not $realPath) { return }
            if (-not (Test-IsValidProjectPath $realPath -Strict)) { return }
            $item = Get-Item $realPath -ErrorAction SilentlyContinue
            if (-not $item) { return }
            if ($seenPath.ContainsKey($realPath)) {
                $idx = $seenPath[$realPath]
                $existing = $projectList[$idx]
                if ($existing.Source -notmatch 'C') {
                    $existing.Source = ($existing.Source + 'C')
                }
                # Claude projects 目录 mtime 通常比 fs 更"近"，取较新的
                if ($_.LastWriteTime -gt $existing.LastWrite) {
                    $existing.LastWrite = $_.LastWriteTime
                    $existing.IsActive  = $true
                }
            } else {
                $seenPath[$realPath] = $projectList.Count
                $projectList.Add([PSCustomObject]@{
                    Path       = $realPath
                    Name       = $item.Name
                    LastWrite  = $_.LastWriteTime
                    IsActive   = $true   # 出现在 claude/projects 即视为活跃
                    Source     = 'C'
                })
            }
        }
    }

    # 3) AtomGit / AtomCode: recent_dirs.txt（按行序=由新到旧）
    $atomRecent = "$env:USERPROFILE\.atomcode\recent_dirs.txt"
    if (Test-Path $atomRecent) {
        $rank = 0
        Get-Content $atomRecent -Encoding UTF8 -ErrorAction SilentlyContinue | ForEach-Object {
            $p = $_.Trim()
            if (-not $p) { return }
            if (-not (Test-IsValidProjectPath $p -Strict)) { return }
            $item = Get-Item $p -ErrorAction SilentlyContinue
            if (-not $item) { return }
            # 给 atomcode 一个伪 mtime：越靠前越新（向前推 1 小时 × rank）
            $pseudoTime = (Get-Date).AddHours(-1 * $rank)
            $rank++
            if ($seenPath.ContainsKey($p)) {
                $idx = $seenPath[$p]
                $existing = $projectList[$idx]
                if ($existing.Source -notmatch 'A') {
                    $existing.Source = ($existing.Source + 'A')
                }
                # AtomGit 的"最近"权重最高
                $existing.LastWrite = $pseudoTime
                $existing.IsActive  = $true
            } else {
                $seenPath[$p] = $projectList.Count
                $projectList.Add([PSCustomObject]@{
                    Path       = $p
                    Name       = $item.Name
                    LastWrite  = $pseudoTime
                    IsActive   = $true
                    Source     = 'A'
                })
            }
        }
    }

    # Fallback: filesystem scan
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
        foreach ($fp in ($fsProjects | Sort-Object LastWriteTime -Descending)) {
            if ($seenPath.ContainsKey($fp.FullName)) { continue }
            if (-not (Test-IsValidProjectPath $fp.FullName -Strict)) { continue }
            $seenPath[$fp.FullName] = $projectList.Count
            $projectList.Add([PSCustomObject]@{
                Path      = $fp.FullName
                Name      = $fp.Name
                LastWrite = $fp.LastWriteTime
                IsActive  = $false
                Source    = ''
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
            $srcBadge = if ($p.Source) { "[{0,-3}]" -f $p.Source } else { '     ' }
            $shortPath = if ($p.Path.Length -gt 45) { '...' + $p.Path.Substring($p.Path.Length - 42) } else { $p.Path }
            Write-Host "    " -NoNewline
            Write-Host $badge -NoNewline -ForegroundColor $badgeColor
            Write-Host "$age  $name  " -NoNewline -ForegroundColor Gray
            Write-Host "$srcBadge " -NoNewline -ForegroundColor Magenta
            Write-Host $shortPath -ForegroundColor DarkGray
        }
    }

    Write-Host ''
    Write-Host '  Legend: K=Kimi  C=Claude  A=AtomGit  G=~/.config/agents' -ForegroundColor DarkGray
    Write-Host "  Type 'kimi' to start · '/skills' to browse · 'dev' to refresh" -ForegroundColor Gray
    Write-Host ''
}

# Auto-run only when this file is invoked directly (not dot-sourced).
if ($MyInvocation.InvocationName -ne '.') {
    Show-AIDashboard @args
}
