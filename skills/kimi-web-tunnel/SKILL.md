---
name: kimi-web-tunnel
description: SolarGlyph 项目 Kimi Code Web UI 远程访问的一键启动/停止与排障。通过 kimi web（--public + token 认证）+ Cloudflare Tunnel 将本地 5490 端口暴露到公网固定域名 https://kimi.newenergycoder.club，实现跨局域网用浏览器/手机远程调试项目。用户说"启动远程访问""开启 kimi 隧道""kimi web 远程""一键启动远程调试""停止远程访问""kimi.newenergycoder.club 打不开"等时使用。
---

# Kimi Web Tunnel — 远程访问一键管理

将本机 Kimi Code Web UI 通过 Cloudflare Tunnel 暴露到公网，实现手机/外地电脑远程调试项目。

## 架构

```
远程浏览器 → https://kimi.newenergycoder.club (Cloudflare CDN)
           → cloudflared 命名隧道 (id: ba13fa49-48be-4d5f-9a13-3e50fb2787c1)
           → http://localhost:5490 (kimi web --public --port 5490)
```

> 端口用 **5490** 而非默认 5494：终端会话里执行 `/web` 会启动一个绑定 `127.0.0.1:5494` 的 LAN-only 实例，若隧道服务也用 5494 会被它抢占（localhost 优先命中 127.0.0.1 绑定），公网报 403 "only local network access is allowed"。专用 5490 彻底避开冲突。

## 快速使用

| 操作 | 命令 / 文件 |
|------|------------|
| 一键启动 | 双击 `scripts/Start-KimiWebTunnel.bat`，或 `pwsh -File scripts/Start-KimiWebTunnel.ps1` |
| 停止 | `pwsh -File scripts/Stop-KimiWebTunnel.ps1` |
| 查日志 | `.devkit/cloudflared/logs/` 下 4 个日志文件 |

脚本幂等：已在运行的组件会跳过（按端口 5490 和 cloudflared 进程名检测），可重复执行。

## 访问地址

- 公网：`https://kimi.newenergycoder.club/?token=<TOKEN>`
- 局域网：`http://<本机IP>:5490/?token=<TOKEN>`
- Token 存于 `.devkit/cloudflared/kimi-web-token.txt`（**勿提交 git**）

## 关键文件

| 文件 | 作用 |
|------|------|
| `.devkit/cloudflared/cloudflared.exe` | 隧道客户端（2026.7.3，从 GitHub release 下载） |
| `.devkit/cloudflared/config.yml` | 隧道 ingress 配置：`kimi.newenergycoder.club → http://localhost:5490` |
| `.devkit/cloudflared/kimi-web-token.txt` | Web UI Bearer Token |
| `D:\Dev_env\Cadence\SPB_Data\.cloudflared\cert.pem` | Cloudflare 账号授权证书（login 产物） |
| `D:\Dev_env\Cadence\SPB_Data\.cloudflared\ba13fa49-*.json` | 隧道凭证（**泄露=域名被劫持，勿外传**） |

## kimi web 启动参数（脚本内置）

```
kimi web --network --public --no-open --port 5490 \
  --auth-token <TOKEN> \
  --allowed-origins "https://kimi.newenergycoder.club"
```

- `--public` 必须：cloudflared 回源时携带访客真实公网 IP（X-Forwarded-For），默认 `--lan-only` 会返回 403 "only local network access is allowed"
- `--public` 模式下 `--restrict-sensitive-apis` 默认启用（禁配置写入/open-in），属预期行为
- 工作目录固定为 `D:\Project_env\SolarGlyph`

## 排障

| 现象 | 排查 |
|------|------|
| 公网 403 "only local network access..." | ① kimi web 没带 `--public`；② 有人在终端跑了 `/web`，其 LAN-only 实例绑定了 `127.0.0.1:5494` 抢占了隧道回源——本 Skill 已改用 5490 规避，若改端口需同步 config.yml |
| 远程看某个会话时 AI 回复不实时更新（要手动刷新） | 该会话正被**终端 CLI** 占用（状态 `prompt_error`）。一个会话同时只能有一个驱动者：终端占用时 Web worker 起不来，只能回放历史。解决：远程直接在 Web UI **新建会话**发任务（流式推送正常）；或先在终端退出该会话再在 Web 里打开接管 |
| 判断会话是否被终端占用 | `GET /api/sessions/?limit=20` 看 `status.reason`：`prompt_error` + 手机端日志出现每几秒轮询 `GET /api/sessions/{id}`（前端 WS 失效后的兼容轮询）|
| 公网 401 | URL 没带 `?token=` 或 token 错误 |
| 公网 522/503 | cloudflared 未运行 → 跑启动脚本；看 `logs/cloudflared.err.log` |
| 公网打不开但本地 5490 正常 | 隧道掉线；确认系统代理未拦截 quic 出站（隧道走 QUIC/UDP7844，可直连无需代理） |
| 端口 5490 被占 | `Get-NetTCPConnection -LocalPort 5490` 找 PID，或跑 Stop 脚本 |
| cloudflared 需重装 | 走代理下载：`curl -L -x http://127.0.0.1:26826 -o cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe`（本机直连 GitHub 会被重置，必须走系统代理 127.0.0.1:26826） |

## 重建隧道（凭证丢失/换域名时）

```powershell
$env:HTTPS_PROXY='http://127.0.0.1:26826'   # login/API 走代理；tunnel run 不需要
cd D:\Project_env\SolarGlyph\.devkit\cloudflared
.\cloudflared.exe tunnel login                                  # 浏览器授权 newenergycoder.club
.\cloudflared.exe tunnel create kimi                            # 记下新 tunnel id
.\cloudflared.exe tunnel route dns kimi kimi.newenergycoder.club
# 同步更新 config.yml 里的 tunnel id 和 credentials-file 路径
```

## 注意

- 两个组件是**分离的隐藏进程**，不依赖任何终端会话；关机/重启后需重新运行启动脚本（如需开机自启可再加计划任务）
- 若曾用 Kimi CLI 后台任务方式启动过服务，先停掉再用脚本，避免端口冲突
