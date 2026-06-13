---
name: fix-everything-windows
description: 修复 Windows 平台 voidtools Everything 搜索工具。涵盖数据库损坏修复、服务重启、筛选器错误排查、进程清理、注册表配置、索引重建等常见故障。当用户说"Everything坏了"、"Everything搜不到文件"、"Everything打不开"、"修复Everything"、"Everything索引坏了"时使用。
---

# Everything 修复 — Windows

> 适用范围: voidtools Everything 桌面搜索工具 | Windows 平台

## 诊断清单

先收集以下信息判断问题类型：

| 问题现象 | 最可能原因 | 处理优先级 |
|----------|-----------|-----------|
| 搜不到文件 | 筛选器(filter)被误设为某类型(如 PICTURE) | P0 立即排查 |
| 搜不到文件 | 数据库损坏(Everything.db corrupt) | P0 立即排查 |
| Everything 打不开 / 闪退 | 服务挂死 / 数据库损坏 | P1 |
| 搜索结果不全 | 索引未包含该目录/卷 | P1 |
| 搜索结果迟缓 | 索引正在重建 / 磁盘繁忙 | P2 |
| 显示"正在索引..." | 正常行为,等索引完成即可 | P3 |

## 工作原理

Everything 由两大组件构成:
- **Everything Service**（后台服务，以 `LocalSystem` 运行，处理 IPC 和文件监控）
- **Everything GUI**（用户界面，连接服务并展示搜索结果）

数据库文件 (`Everything.db`) 默认存储在 `%LOCALAPPDATA%\Everything\`。索引在 GUI 第一次连接服务时触发构建，数据库在索引完成或关闭 GUI 时写入磁盘。

## 故障处理工作流

### 1. 环境检查

```powershell
# 检查安装目录
dir "C:\Program Files\Everything" 2>nul || dir "C:\Program Files (x86)\Everything"

# 检查服务状态
sc query Everything | findstr "STATE"

# 检查进程状态
tasklist /fi "imagename eq Everything.exe" /v

# 查看所有 Everything 进程详情 (识别 Not Responding 僵尸进程)
tasklist /fi "imagename eq Everything.exe" /v

# 检查数据库文件
dir "%LOCALAPPDATA%\Everything\*.db"

# 检查配置文件
type "%APPDATA%\Everything\Everything.ini" | findstr /i "filter db_location"

# 检查安装目录配置文件(可能含 run_as_admin 等设置)
type "C:\Program Files (x86)\Everything\Everything.ini"
```

### 2. 常见问题定位

#### 2.1 筛选器(filter)被锁定为某类型

**现象**: Everything 正常运行但只显示某一类文件（如图片），其他文件搜不到。

**排查**:
```powershell
findstr "filter=" "%APPDATA%\Everything\Everything.ini"
# 若输出类似 filter=PICTURE / filter=DOCUMENT，则为筛选器问题
```

**修复**: 修改配置文件中的 `filter=` 为 `EVERYTHING`。
```ini
; 编辑 %APPDATA%\Everything\Everything.ini
filter=EVERYTHING
```
修改后重启 Everything GUI 即可生效，**无需重建索引**。

#### 2.2 数据库损坏

**现象**: Everything 服务运行但 GUI 无响应 / 搜索结果异常 / 搜不到文件。

**排查**:
```powershell
# 检查 GUI 是否响应
tasklist /fi "imagename eq Everything.exe" /v
# 如有 "Not Responding" 状态的进程，说明 GUI 挂死
```

**修复流程**:

**步骤 1: 停止 Everything 服务(需管理员权限)**
```powershell
# 通过 UAC 提权
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c sc stop Everything && timeout /t 2 /nobreak >nul'" -WindowStyle Hidden -Wait
```

**步骤 2: 删除损坏的数据库**
```powershell
del /f /q "%LOCALAPPDATA%\Everything\Everything.db"
```

**步骤 3: 启动服务**
```powershell
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c sc start Everything'" -WindowStyle Hidden -Wait
```

**步骤 4: 启动 GUI 触发索引重建**
```powershell
powershell -Command "Start-Process 'C:\Program Files (x86)\Everything\Everything.exe'"
```

> ⚠ 索引重建可能需要 **3-10 分钟**（取决于文件数量）。期间 Everything GUI 会占用大量内存和 CPU，这是正常现象。

#### 2.3 进程挂死（多实例/僵尸进程）

**现象**: 有多个 Everything.exe 进程，部分状态为 "Not Responding"。

**定位**:
```powershell
tasklist /fi "imagename eq Everything.exe" /v
# 检查 PID、会话、状态、用户名
```

**修复**:
```powershell
# 先用 wmic 杀掉非系统进程(无需管理员)
wmic process where "name='Everything.exe'" call terminate

# 再用管理员停服务
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c sc stop Everything && timeout /t 2 /nobreak >nul'" -WindowStyle Hidden -Wait

# 重新启动服务
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c sc start Everything'" -WindowStyle Hidden -Wait

# 启动 GUI
powershell -Command "Start-Process 'C:\Program Files (x86)\Everything\Everything.exe'"
```

#### 2.4 服务丢失 / 无法启动

**现象**: `sc query Everything` 返回 1060（服务未安装）。

**修复**:
```powershell
# 重新安装 Everything 服务
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c \"\"C:\Program Files (x86)\Everything\Everything.exe\" -install-service\"'" -WindowStyle Hidden -Wait
```

#### 2.5 索引未包含目标盘符

**现象**: 某盘文件搜不到。

**排查**: 检查配置中 NTFS 卷包含情况。
```powershell
findstr "ntfs_volume_include" "%APPDATA%\Everything\Everything.ini"
```

**修复**: 在 Everything GUI 中进入 Tools → Options → NTFS → 勾选缺失的盘符 → Apply。

### 3. 配置文件关键字段说明

| 字段 | 说明 | 常见错误值 |
|------|------|-----------|
| `filter=` | 当前筛选器类型 | `PICTURE` / `DOCUMENT` / `AUDIO` / `VIDEO` |
| `db_location=` | 数据库路径(空=默认) | 错误的路径导致 DB 无法保存 |
| `run_as_admin=` | 是否以管理员运行 | 设为 1 会触发 UAC 弹窗 |
| `index_size=` | 是否索引文件大小 | 0=不索引, 1=索引 |
| `http_server_enabled=` | HTTP 服务 | 0=禁用, 1=启用 |

用户配置文件: `%APPDATA%\Everything\Everything.ini`
安装目录配置: `C:\Program Files (x86)\Everything\Everything.ini` (`app_data=1` 时后者仅存少量启动设置)

### 4. 验证修复

```powershell
# 1. 确认服务运行
sc query Everything | findstr "STATE"
# 期望: STATE : 4 RUNNING

# 2. 确认 GUI 进程正常
tasklist /fi "imagename eq Everything.exe" /v
# 期望: 只有 1 个 GUI 进程(用户态) + 1 个服务进程(系统态), 状态均为 Running

# 3. 确认 GUI 窗口响应
powershell -Command "(Get-Process -Name Everything).Responding"
# 期望: True

# 4. 手动测试: 在 Everything 搜索框输入任意文件名
# 期望: 显示搜索结果
```

## 注意事项

1. **管理员权限**: 停止/启动 Everything 服务需要管理员权限。使用 `Start-Process -Verb RunAs` 提权。
2. **数据库文件**: `Everything.db` 删除后会自动重建，但索引重建期间搜索不完整。
3. **不要在 Everything GUI 运行时修改 `Everything.ini`** — 配置修改会被 GUI 退出时的保存覆盖。
4. **`run_as_admin=1` 的影响**: GUI 启动时会弹 UAC 提权，若用户未确认则进程可能挂起显示 "Not Responding"。
5. **数据库写入时机**: Everything 在索引完成后或 GUI 退出时写入 `Everything.db`，不会实时写入。
