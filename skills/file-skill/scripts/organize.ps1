#Requires -Version 3.0
<#
.SYNOPSIS
    Desktop/Directory File Organizer (PowerShell)
.DESCRIPTION
    Zero deletion / zero overwrite policy.
    Permission pre-check, large file filtering, smart scanning.
    Generates a structured JSON operation log for rollback support.
#>
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$TargetDir,

    [double]$SizeThreshold = 1,

    [string[]]$Whitelist = @(),

    [switch]$DryRun,

    [ValidateSet("phase1","phase2","all")]
    [string]$Phase = "all"
)

# Force UTF-8 output
if ($PSVersionTable.PSVersion.Major -ge 6) {
    $OutputEncoding = [System.Text.Encoding]::UTF8
} else {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
}

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

$SHORTCUT_EXTENSIONS = @(".lnk", ".app", ".url", ".webloc", ".desktop")

$SYSTEM_SKIP_EXTENSIONS = @(".lnk", ".app", ".ds_store", ".desktop.ini", ".localized")

$SYSTEM_SKIP_NAMES = @(
    "desktop.ini", ".DS_Store", ".localized", "Thumbs.db",
    ".com.apple.timemachine.donotpresent"
)

# Category map - extension to category name
$CATEGORY_MAP = @{}
$CATEGORY_MAP["图片"] = @(".png",".jpg",".jpeg",".gif",".bmp",".tiff",".webp",".svg",".ico",".heic",".heif")
$CATEGORY_MAP["文档"] = @(".docx",".pdf",".txt",".doc",".ppt",".pptx",".odt",".rtf",".pages")
$CATEGORY_MAP["表格"] = @(".xlsx",".csv",".xls",".numbers",".ods",".tsv")
$CATEGORY_MAP["安装包"] = @(".exe",".dmg",".pkg",".msi",".apk",".deb",".rpm",".appimage")
$CATEGORY_MAP["音频"] = @(".mp3",".wav",".flac",".m4a",".ogg",".aac",".wma",".aiff")
$CATEGORY_MAP["视频"] = @(".mp4",".avi",".mov",".mkv",".flv",".wmv",".webm",".m4v",".ts")
$CATEGORY_MAP["压缩包"] = @(".zip",".rar",".7z",".tar",".gz",".bz2",".xz",".tgz",".tar.gz")
$CATEGORY_MAP["日志"] = @(".log")
$CATEGORY_MAP["代码"] = @(".py",".js",".ts",".jsx",".tsx",".java",".c",".cpp",".h",".hpp",".cs",".go",".rb",".php",".swift",".kt",".rs",".lua",".sh",".bat",".ps1",".html",".css",".scss",".less",".json",".xml",".yaml",".yml",".sql",".r",".md",".ini",".cfg",".conf",".toml")
$CATEGORY_MAP["字体"] = @(".ttf",".otf",".woff",".woff2",".eot")
$CATEGORY_MAP["电子书"] = @(".epub",".mobi",".azw3",".djvu")
$CATEGORY_MAP["设计文件"] = @(".psd",".ai",".sketch",".fig",".xd",".indd")

# Reverse lookup: extension -> category
$EXT_TO_CATEGORY = @{}
foreach ($cat in $CATEGORY_MAP.Keys) {
    foreach ($ext in $CATEGORY_MAP[$cat]) {
        $EXT_TO_CATEGORY[$ext] = $cat
    }
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Test-IsShortcut {
    param([System.IO.FileInfo]$File)
    $ext = $File.Extension.ToLower()
    return ($SHORTCUT_EXTENSIONS -contains $ext)
}

function Test-IsSystemFile {
    param([System.IO.FileInfo]$File)
    $name = $File.Name
    $ext = $File.Extension.ToLower()
    if ($SYSTEM_SKIP_NAMES -contains $name) { return $true }
    if ($SYSTEM_SKIP_EXTENSIONS -contains $ext) { return $true }
    if ($name.StartsWith(".")) { return $true }
    return $false
}

function Test-IsFileLocked {
    param([System.IO.FileInfo]$File)
    try {
        $stream = [System.IO.File]::Open($File.FullName, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        $stream.Close()
        return $false
    } catch {
        return $true
    }
}

function Get-FileSizeGB {
    param([System.IO.FileInfo]$File)
    try { return $File.Length / [math]::Pow(1024, 3) }
    catch { return 0.0 }
}

function Get-UnixTime {
    param([datetime]$DateTime)
    try {
        $epoch = [datetime]::new(1970,1,1,0,0,0,[System.DateTimeKind]::Utc)
        return [long]($DateTime.ToUniversalTime() - $epoch).TotalSeconds
    } catch { return 0 }
}

function Invoke-SafeMove {
    param(
        [string]$SrcPath,
        [string]$DstDir,
        [bool]$IsDryRun = $false
    )
    if (-not (Test-Path -LiteralPath $DstDir)) {
        if (-not $IsDryRun) {
            New-Item -ItemType Directory -Path $DstDir -Force | Out-Null
        }
    }
    $srcFile = Get-Item -LiteralPath $SrcPath
    $dstPath = Join-Path $DstDir $srcFile.Name

    if (Test-Path -LiteralPath $dstPath) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($srcFile.Name)
        $sfx = $srcFile.Extension
        $counter = 1
        while (Test-Path -LiteralPath $dstPath) {
            $dstPath = Join-Path $DstDir "${stem}_${counter}${sfx}"
            $counter++
        }
    }

    if (-not $IsDryRun) {
        Move-Item -LiteralPath $SrcPath -Destination $dstPath -Force
    }
    return $dstPath
}

function Test-KeywordMatchFolder {
    param([string]$FileStem, [string]$FolderName)
    $fnLower = $FileStem.ToLower()
    $fdLower = $FolderName.ToLower()
    if ($fdLower.Length -lt 2) { return $false }
    return $fnLower.Contains($fdLower)
}

function Test-NamingPatternMatch {
    param([string]$FileStem, [string[]]$ExistingStems)
    if (-not $ExistingStems -or $ExistingStems.Count -eq 0) { return $false }
    $matchCount = 0
    foreach ($es in $ExistingStems) {
        $commonLen = 0
        $minLen = [math]::Min($FileStem.Length, $es.Length)
        for ($i = 0; $i -lt $minLen; $i++) {
            if ($FileStem[$i] -eq $es[$i]) { $commonLen++ }
            else { break }
        }
        if ($commonLen -ge 3) { $matchCount++ }
    }
    return ($matchCount -ge 2)
}

function Get-CategoryByExtension {
    param([string]$Extension)
    $ext = $Extension.ToLower()
    if ($EXT_TO_CATEGORY.ContainsKey($ext)) { return $EXT_TO_CATEGORY[$ext] }
    return "其他文件"
}

# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------

function Get-ExistingFolders {
    param([string]$TargetPath)
    $folders = @{}
    Get-ChildItem -LiteralPath $TargetPath -Directory -ErrorAction SilentlyContinue | Where-Object { -not $_.Name.StartsWith(".") } | ForEach-Object {
        $folders[$_.Name] = $_.FullName
    }
    return $folders
}

function Get-FolderFileStems {
    param([string]$FolderPath)
    $stems = [System.Collections.ArrayList]@()
    try {
        Get-ChildItem -LiteralPath $FolderPath -File -ErrorAction SilentlyContinue | ForEach-Object {
            [void]$stems.Add([System.IO.Path]::GetFileNameWithoutExtension($_.Name))
        }
    } catch {}
    return @($stems)
}

function Invoke-ScanCandidates {
    param(
        [string]$TargetPath,
        [double]$SizeThresholdGB,
        [string[]]$WhitelistSet,
        [hashtable]$Log
    )
    $candidates = [System.Collections.ArrayList]@()
    $files = Get-ChildItem -LiteralPath $TargetPath -File -ErrorAction SilentlyContinue

    foreach ($entry in $files) {
        $name = $entry.Name

        if ($WhitelistSet -contains $name) {
            $skipItem = @{}
            $skipItem["file"] = $name
            $skipItem["path"] = $entry.FullName
            $skipItem["reason"] = "用户白名单豁免"
            $Log.skipped += @($skipItem)
            continue
        }

        if (Test-IsShortcut $entry) {
            $skipItem = @{}
            $skipItem["file"] = $name
            $skipItem["path"] = $entry.FullName
            $skipItem["reason"] = "快捷方式/别名，禁止移动"
            $Log.skipped += @($skipItem)
            continue
        }

        if (Test-IsSystemFile $entry) {
            $skipItem = @{}
            $skipItem["file"] = $name
            $skipItem["path"] = $entry.FullName
            $skipItem["reason"] = "系统文件，自动跳过"
            $Log.skipped += @($skipItem)
            continue
        }

        $sizeGB = Get-FileSizeGB $entry
        if ($sizeGB -gt $SizeThresholdGB) {
            $errItem = @{}
            $errItem["file"] = $name
            $errItem["path"] = $entry.FullName
            $errItem["reason"] = "文件大小 $([math]::Round($sizeGB,2)) GB（超过 $SizeThresholdGB GB 阈值）"
            $errItem["suggestion"] = "建议手动移入对应分类文件夹"
            $Log.errors += @($errItem)
            continue
        }

        if (Test-IsFileLocked $entry) {
            $errItem = @{}
            $errItem["file"] = $name
            $errItem["path"] = $entry.FullName
            $errItem["reason"] = "文件被占用，无法移动"
            $errItem["suggestion"] = "关闭占用该文件的程序后重试"
            $Log.errors += @($errItem)
            continue
        }

        $item = @{}
        $item["path"] = $entry.FullName
        $item["name"] = $name
        $item["stem"] = [System.IO.Path]::GetFileNameWithoutExtension($name)
        $item["ext"] = $entry.Extension.ToLower()
        $item["size"] = $entry.Length
        $item["atime"] = (Get-UnixTime $entry.LastAccessTime)
        $item["mtime"] = (Get-UnixTime $entry.LastWriteTime)
        [void]$candidates.Add($item)
    }

    return @($candidates)
}

function Invoke-MatchExistingFolders {
    param(
        [array]$CandidateFiles,
        [hashtable]$ExistingFolders,
        [hashtable]$FolderStemsCache,
        [hashtable]$Log,
        [bool]$IsDryRun
    )
    $unmatched = [System.Collections.ArrayList]@()
    $statusVal = if ($IsDryRun) { "dry_run" } else { "done" }

    foreach ($finfo in $CandidateFiles) {
        $matched = $false

        foreach ($folderName in @($ExistingFolders.Keys)) {
            if (Test-KeywordMatchFolder $finfo.stem $folderName) {
                $dst = Invoke-SafeMove -SrcPath $finfo.path -DstDir $ExistingFolders[$folderName] -IsDryRun $IsDryRun
                $opItem = @{}
                $opItem["file"] = $finfo.name
                $opItem["original_path"] = $finfo.path
                $opItem["destination_path"] = $dst
                $opItem["destination_folder"] = $folderName
                $opItem["method"] = "关键词匹配已有文件夹"
                $opItem["confidence"] = "high"
                $opItem["status"] = $statusVal
                $Log.operations += @($opItem)
                $Log.summary.auto_organized++
                $matched = $true
                break
            }
        }
        if ($matched) { continue }

        foreach ($folderName in @($FolderStemsCache.Keys)) {
            $stems = $FolderStemsCache[$folderName]
            if (Test-NamingPatternMatch $finfo.stem $stems) {
                $folderPath = $ExistingFolders[$folderName]
                $dst = Invoke-SafeMove -SrcPath $finfo.path -DstDir $folderPath -IsDryRun $IsDryRun
                $opItem = @{}
                $opItem["file"] = $finfo.name
                $opItem["original_path"] = $finfo.path
                $opItem["destination_path"] = $dst
                $opItem["destination_folder"] = $folderName
                $opItem["method"] = "命名规律匹配已有文件夹"
                $opItem["confidence"] = "high"
                $opItem["status"] = $statusVal
                $Log.operations += @($opItem)
                $Log.summary.auto_organized++
                $matched = $true
                break
            }
        }

        if (-not $matched) {
            [void]$unmatched.Add($finfo)
        }
    }

    return @($unmatched)
}

function Invoke-FallbackClassify {
    param(
        [array]$Unmatched,
        [string]$TargetPath,
        [hashtable]$Log,
        [bool]$IsDryRun
    )

    $epoch = [datetime]::new(1970,1,1,0,0,0,[System.DateTimeKind]::Utc)
    $now = [long]([datetime]::UtcNow - $epoch).TotalSeconds
    $sixtyDays = 60 * 86400
    $statusVal = if ($IsDryRun) { "dry_run" } else { "done" }

    $infrequentFiles = [System.Collections.ArrayList]@()
    $remainingFiles = [System.Collections.ArrayList]@()

    foreach ($finfo in $Unmatched) {
        if (($now - $finfo.atime) -gt $sixtyDays) {
            [void]$infrequentFiles.Add($finfo)
        } else {
            [void]$remainingFiles.Add($finfo)
        }
    }

    if ($infrequentFiles.Count -ge 2) {
        $infrequentFolderName = "不常用文件"
        $destFolder = Join-Path $TargetPath $infrequentFolderName
        $alreadyCreated = $Log.created_folders | Where-Object { $_.folder_name -eq $infrequentFolderName }
        if (-not (Test-Path -LiteralPath $destFolder) -and -not $alreadyCreated) {
            $cfItem = @{}
            $cfItem["folder_name"] = $infrequentFolderName
            $cfItem["path"] = $destFolder
            $cfItem["created_at"] = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
            $Log.created_folders += @($cfItem)
        }
        foreach ($finfo in $infrequentFiles) {
            $dst = Invoke-SafeMove -SrcPath $finfo.path -DstDir $destFolder -IsDryRun $IsDryRun
            $opItem = @{}
            $opItem["file"] = $finfo.name
            $opItem["original_path"] = $finfo.path
            $opItem["destination_path"] = $dst
            $opItem["destination_folder"] = $infrequentFolderName
            $opItem["method"] = "不常用文件归类（超过60天未使用）"
            $opItem["confidence"] = "high"
            $opItem["status"] = $statusVal
            $Log.operations += @($opItem)
            $Log.summary.auto_organized++
        }
    } else {
        foreach ($f in $infrequentFiles) { [void]$remainingFiles.Add($f) }
    }

    foreach ($finfo in $remainingFiles) {
        $folderName = Get-CategoryByExtension $finfo.ext
        $destFolder = Join-Path $TargetPath $folderName
        $alreadyCreated = $Log.created_folders | Where-Object { $_.folder_name -eq $folderName }
        if (-not (Test-Path -LiteralPath $destFolder) -and -not $alreadyCreated) {
            $cfItem = @{}
            $cfItem["folder_name"] = $folderName
            $cfItem["path"] = $destFolder
            $cfItem["created_at"] = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
            $Log.created_folders += @($cfItem)
        }
        $dst = Invoke-SafeMove -SrcPath $finfo.path -DstDir $destFolder -IsDryRun $IsDryRun
        $opItem = @{}
        $opItem["file"] = $finfo.name
        $opItem["original_path"] = $finfo.path
        $opItem["destination_path"] = $dst
        $opItem["destination_folder"] = $folderName
        $opItem["method"] = "按文件类型分类"
        $opItem["confidence"] = "high"
        $opItem["status"] = $statusVal
        $Log.operations += @($opItem)
        $Log.summary.auto_organized++
    }
}

function Save-OrganizeLog {
    param(
        [hashtable]$Log,
        [string]$TargetPath,
        [bool]$IsDryRun
    )
    $Log.summary.skipped_count = @($Log.skipped).Count
    $Log.summary.error_count = @($Log.errors).Count
    $Log.summary.created_folder_count = @($Log.created_folders).Count

    $logDir = Join-Path $TargetPath ".file_organizer_logs"
    if (-not (Test-Path -LiteralPath $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFilename = "organize_${ts}.json"
    $logPath = Join-Path $logDir $logFilename

    if (-not $IsDryRun) {
        $Log | ConvertTo-Json -Depth 10 | Out-File -FilePath $logPath -Encoding UTF8
    }
    $Log["log_file"] = $logPath
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

$targetResolved = (Resolve-Path -LiteralPath $TargetDir -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath $targetResolved -PathType Container)) {
    Write-Output (@{ error = "Target directory does not exist: $targetResolved" } | ConvertTo-Json -Depth 5)
    exit 1
}

$whitelistSet = $Whitelist

$log = @{
    timestamp         = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    target_dir        = $targetResolved
    size_threshold_gb = $SizeThreshold
    dry_run           = [bool]$DryRun
    phase             = $Phase
    operations        = @()
    skipped           = @()
    errors            = @()
    created_folders   = @()
    summary           = @{
        total_scanned        = 0
        auto_organized       = 0
        skipped_count        = 0
        error_count          = 0
        created_folder_count = 0
    }
}

$existingFolders = Get-ExistingFolders $targetResolved
$folderStemsCache = @{}
foreach ($fname in @($existingFolders.Keys)) {
    $folderStemsCache[$fname] = Get-FolderFileStems $existingFolders[$fname]
}

if ($Phase -eq "phase2") {
    $candidateFiles = Invoke-ScanCandidates -TargetPath $targetResolved -SizeThresholdGB $SizeThreshold -WhitelistSet $whitelistSet -Log $log
    $log.summary.total_scanned = @($candidateFiles).Count
    Invoke-FallbackClassify -Unmatched $candidateFiles -TargetPath $targetResolved -Log $log -IsDryRun ([bool]$DryRun)
    Save-OrganizeLog -Log $log -TargetPath $targetResolved -IsDryRun ([bool]$DryRun)
    Write-Output ($log | ConvertTo-Json -Depth 10)
    exit 0
}

# Phase 1 or all
$candidateFiles = Invoke-ScanCandidates -TargetPath $targetResolved -SizeThresholdGB $SizeThreshold -WhitelistSet $whitelistSet -Log $log
$log.summary.total_scanned = @($candidateFiles).Count

$unmatched = Invoke-MatchExistingFolders -CandidateFiles $candidateFiles -ExistingFolders $existingFolders -FolderStemsCache $folderStemsCache -Log $log -IsDryRun ([bool]$DryRun)

if ($Phase -eq "phase1") {
    $log["unmatched_files"] = @()
    foreach ($finfo in $unmatched) {
        $umItem = @{}
        $umItem["file"] = $finfo.name
        $umItem["path"] = $finfo.path
        $umItem["ext"] = $finfo.ext
        $umItem["size"] = $finfo.size
        $umItem["atime"] = $finfo.atime
        $umItem["mtime"] = $finfo.mtime
        $log["unmatched_files"] += @($umItem)
    }
    $log["existing_folders"] = @($existingFolders.Keys)
    Save-OrganizeLog -Log $log -TargetPath $targetResolved -IsDryRun ([bool]$DryRun)
    Write-Output ($log | ConvertTo-Json -Depth 10)
    exit 0
}

# phase == "all"
Invoke-FallbackClassify -Unmatched $unmatched -TargetPath $targetResolved -Log $log -IsDryRun ([bool]$DryRun)
Save-OrganizeLog -Log $log -TargetPath $targetResolved -IsDryRun ([bool]$DryRun)
Write-Output ($log | ConvertTo-Json -Depth 10)
