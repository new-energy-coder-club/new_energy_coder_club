---
name: feishu-multi-tenant
description: 飞书多企业账号接入与移植流程（lark-cli 多 profile + .env 应用凭证）。用户说"配置飞书""接入另一个企业""加飞书账号""lark-cli 登录""FEISHU_APP_ID 拉字段 99991672""多维表格跨企业""飞书凭证没权限""移植飞书应用"时使用。覆盖：双/多企业 profile 并存、user 扫码授权、bot 身份 scope 补齐、.env 凭证写库与验证。核心陷阱：自建应用不能跨企业授权（必须对方企业自建应用）；user 身份有 scope ≠ bot 身份有；bot 加 scope 后需重新发布版本才生效。
---

# 飞书多企业账号接入 Skill

把"配置一个能用的飞书企业身份"标准化成可重复流程，支持**多企业并存**。本流程在 SolarGlyph 项目实测通过（默认企业 cli_a94c + 天合 TrinaCLI cli_aaf3）。

## 三种身份/信息源，先分清

| 信息源 | 身份 | 用途 | 凭据位置 |
|---|---|---|---|
| **lark-cli user** | 个人用户 | 读写个人资源（日历/邮箱/我的文档）、扫码即得全部授权 scope | `~/.lark-cli/config.json` |
| **lark-cli bot** | 应用机器人 | 命令行走 tenant token | 同上 |
| **.env 凭证** | 应用机器人 | 项目脚本/后端直接调 Open API（拉字段/记录） | `项目/.env` 的 `FEISHU_APP_ID/SECRET` |

> ⚠️ **最常踩的坑**：user 身份扫码时拿到了一堆 scope，但 **bot/tenant 身份是独立授权**——所以"lark-cli 能读、.env 脚本 99991672"是常态，要去开放平台单独给 bot 开 scope（见第 4 步）。

---

## 标准流程（按顺序）

### 1. 安装 / 修复 lark-cli

```bash
npm install -g @larksuite/cli@latest   # 提供 lark-cli 命令
lark-cli update                        # 同步 Agent Skills 到二进制版本（版本不一致会提示）
lark-cli --version
```

### 2. 追加一个企业 profile（不覆盖现有）

每个企业 = 一个**对方企业下的自建应用**。拿到该应用的 App ID/Secret 后追加为命名 profile：

```bash
printf '%s' '<APP_SECRET>' | lark-cli config init \
  --app-id <cli_xxx> --app-secret-stdin \
  --brand feishu --name <企业名> --lang zh
```

- `--app-secret-stdin`：密钥走标准输入，不进命令行/进程列表（安全）
- `--name`：追加命名 profile，**不覆盖**已有配置
- 验证：`lark-cli profile list` 应看到新旧两个 profile，旧的 active 不变

### 3. user 扫码授权（设备流，10 分钟有效）

```bash
# 推荐 AI 非阻塞流程：先拿二维码
lark-cli auth login --recommend --no-wait --json --profile <企业名>
#  → 输出 verification_url + device_code
lark-cli auth qrcode "<verification_url>" --output ./qr.png   # 生成二维码给用户扫
# 用户扫码确认后收尾：
lark-cli auth login --profile <企业名> --device-code <device_code>
```

**坑**：`device_code` 仅 10 分钟有效，跨轮对话极易过期（实测连废 3 个）。**最稳做法是让用户在自己终端就地跑**：

```
!lark-cli auth login --profile <企业名> --recommend
```

（`!` 前缀在会话内就地执行，扫完即完成，无时间差。）成功标志：`lark-cli profile list` 该 profile 出现用户名 + token valid。

### 4. 补齐 bot 身份 scope（.env 脚本能用 key 的关键）

user 授权 ≠ bot 授权。先用 .env 凭证实测，看缺哪个 scope：

```bash
node scripts/feishu_bitable_fields.mjs <base_token> <table_id>
```

报 `99991672 Access denied` 时，错误体会带**直达申请链接**，形如：

```
https://open.feishu.cn/app/<app_id>/auth?q=bitable:app:readonly,bitable:app,base:field:read&token_type=tenant
```

让用户（该企业、有应用管理权限的账号）打开链接勾选开通。
读多维表常用：`base:field:read` + `bitable:app:readonly`（要读记录再加 `base:record:read`）。

> ⚠️ **自建应用给 bot 加 scope 后通常要重新发布版本才生效**（版本管理与发布 → 创建版本 → 发布，管理员审批）。

### 5. 写入项目 .env 并验证

```bash
# .env 中找到/新增两行（值不要进 git，.env 已被 .gitignore 覆盖）
FEISHU_APP_ID=<cli_xxx>
FEISHU_APP_SECRET=<secret>
```

验证（必须跑出真实字段才算通）：

```bash
node scripts/feishu_bitable_fields.mjs <base_token> <table_id>
# 期望：✅ 共 N 个字段 + 字段名列表
```

---

## 跨企业授权铁律

- **企业自建应用只能给本企业成员授权**。要操作"别的企业"的飞书，必须在**对方企业**单独建一个自建应用（需要对方企业成员+开发者权限），再按上面 2–5 步接入。
- 想让一个应用服务多企业 → 得改成**应用商店应用**上架、由对方企业管理员安装（流程重、需审核），一般项目不建议。
- 每个企业一套 `(App ID, App Secret)` + 一个命名 profile，互不干扰。

## 多身份调用

```bash
lark-cli <cmd>                        # 默认走 active profile
lark-cli <cmd> --profile <企业名>      # 指定企业
lark-cli profile use <企业名>          # 切换默认生效 profile（use - 切回）
lark-cli whoami --profile <企业名>     # 查当前身份
lark-cli base +record-list --base-token <bt> --table-id <tid> --profile <企业名>   # 读多维表记录
```

## 验证清单（交付前逐项打勾）

- [ ] `lark-cli profile list`：目标企业 profile 存在、user 已登录、token valid
- [ ] `node scripts/feishu_bitable_fields.mjs`：bot 身份拉出字段（证明 .env + scope 都通）
- [ ] `.env` 两行的值非空且未被提交（`git status` 不应出现 `.env`）

## 参考脚本

- `scripts/feishu_bitable_fields.mjs` — 用 .env 凭证走 bot 身份拉指定表字段（排障/验证首选）

## 已知故障速查

| 报错 | 原因 | 解法 |
|---|---|---|
| `99991672 Access denied ... base:field:read` | bot 身份缺 scope | 第 4 步：开 scope + 重新发布版本 |
| `device_code is invalid` | 扫码超 10 分钟 | 让用户终端就地跑 `!lark-cli auth login` |
| 扫码提示"应用不可用/不在可用范围" | 用本企业应用给外企业授权 | 铁律：必须在对方企业自建应用 |
| user 能读、脚本 99991672 | user/bot 授权独立 | 给 bot 单独开 scope（第 4 步） |
