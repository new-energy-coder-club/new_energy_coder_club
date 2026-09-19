---
name: ark-plan-auth-doctor
version: 1.0.0
description: 火山引擎方舟 Agent Plan / Coding Plan 调用报 401(The API key or AK/SK in the request is missing or invalid)时的定位与修复 playbook。当用户遇到 provider.auth_error、HTTP 401、API key missing or invalid、Claude Code / Kimi Code / cc-switch / OpenAI 兼容客户端接入 ark.cn-beijing.volces.com 失败、方舟 Key 换了环境就不通等问题时触发。核心能力:curl 矩阵实测绕过客户端、请求 ID 时间戳解码区分"服务端瞬时故障 vs 客户端确定性错误"、报错文案指纹比对精准定位(Key 失效 / Base URL 缺 /plan 路径 / 认证头格式错误)、一键诊断脚本。命中关键词:方舟 401 / ark 401 / Agent Plan 401 / plan key 无效 / ark-cn-beijing 401 / claude code 火山 401 / 火山引擎 API key invalid。
---

# ARK Plan 401 诊断医生 (ark-plan-auth-doctor)

定位火山引擎方舟 **Agent Plan / Coding Plan** 调用 401 的根因并给出修复动作。这套流程从真实案例沉淀:Key 实测有效但客户端持续 401,最终靠**报错文案指纹**锁定为客户端 Base URL 缺少 `/plan` 路径。

## 核心结论(先看这个)

> **Plan 专用 Key 只被 `/api/plan/*` 路由认可。** 把它发到普通方舟端点 `/api/v3/*`、或其他任何非 plan 路径,网关一律回 401 `The API key or AK/SK in the request is missing or invalid.`——文案和"Key 失效"完全一样,极易误判。
> 同理,普通方舟 API Key / Coding Plan Key 拿到 `/api/plan/*` 下也用不了(官方文档明确:其他方舟 API Key 无法在 Agent Plan 中使用)。

正确端点:

| 协议 | Base URL | 路径 |
|---|---|---|
| OpenAI 兼容 | `https://ark.cn-beijing.volces.com/api/plan/v3` | `POST {base}/chat/completions`,头 `Authorization: Bearer <key>` |
| Anthropic 兼容 | `https://ark.cn-beijing.volces.com/api/plan` | `POST {base}/v1/messages`,头 `x-api-key: <key>` + `anthropic-version: 2023-06-01` |

## 排查流程(5 步)

### 第 1 步:收集信息

向用户索取:完整报错原文(含 Request id)、出错的客户端/工具及版本、该客户端配置的 base URL、Key(只需前 8 位 + 后 6 位脱敏形式)。**全程不要回显完整 Key。**

### 第 2 步:绕过客户端,curl 直测 Key

```bash
KEY="<ark-api-key>"
# OpenAI 兼容
curl -sS -X POST "https://ark.cn-beijing.volces.com/api/plan/v3/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KEY" \
  -d '{"model":"ark-code-latest","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
# Anthropic 兼容
curl -sS -X POST "https://ark.cn-beijing.volces.com/api/plan/v1/messages" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-sonnet-4-5","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

- 返回 200 → Key 有效,**问题 100% 在客户端配置**,进第 3 步指纹比对;
- 返回 401 `The API key doesn't exist.` → Key 已被删除/轮换,去控制台重建,流程结束。

### 第 3 步:请求 ID 时间戳解码(区分瞬时故障 vs 确定性错误)

火山网关 Request id 格式:`02` + 10 位秒级时间戳 + 随机串。取第 3~12 位即请求时间:

```bash
id="021789809039613fc7578b59e843c90e5af4aa62e8cfda965e91e"
echo "$id" | cut -c3-12          # → 1789809039(unix 秒)
date -d "@1789809039"            # 可读时间
```

- 失败请求与"刚实测的成功请求"**时间交错**(相差几分钟内)→ 不是服务端故障,是客户端发出去的请求本身有问题,指纹比对必能命中;
- 失败集中在某个时间窗、之后自愈 → 可能是火山侧鉴权抖动,重试即可。

### 第 4 步:报错文案指纹比对(核心)

让用户提供客户端收到的**原始报错文案**,或运行诊断脚本,按下表命中:

| 场景 | 服务端返回 | 含义 / 修复 |
|---|---|---|
| ✅ 正确路径 + Bearer | HTTP 200 | Key 有效,基线 |
| ❌ Plan Key 打到 `/api/v3/*`(普通端点) | 401 `The API key or AK/SK in the request is missing or invalid.`(**大写 The,大写 Request id**) | **Base URL 缺少 `/plan`**,最高频根因。改 base 为 `…/api/plan` 或 `…/api/plan/v3` |
| ❌ 不带 Authorization 头 | 401 `the API key or AK/SK ...`(**小写 the,小写 request id**) | 客户端没把 Key 发出去:环境变量未生效、被其他配置覆盖、配置文件没保存 |
| ❌ Authorization 缺 `Bearer ` 前缀 | 同上,小写 | 认证头格式错误,补 `Bearer ` |
| ❌ Key 不存在 / 已轮换 / 已删除 | 401 `The API key doesn't exist.` | Key 失效。去[方舟控制台](https://console.volcengine.com/ark)重建;客户端全量替换旧 Key |
| 国内站 Key 打到国际站 `ark.ap-southeast.volces.com` | 401 `The API key doesn't exist.` | 区域不匹配,域名改回 `ark.cn-beijing.volces.com` |
| Key 首尾带空格 | 仍然 200 | 服务端自动 trim——可排除"复制带空格"这个猜测,别浪费时间 |
| OpenAI 客户端自动拼 `/v1` → `/api/plan/v1/chat/completions` | 200 | plan 网关兼容;只要 base 里有 `/plan` 就能工作 |

**判读要点:**用户报错是大写 `The API key...missing or invalid` + 大写 `Request id`,而 curl 直测同 Key 秒级通过——基本可断定是"Key 打到了非 plan 路径"。

### 第 5 步:修复与验证

1. 改客户端 base URL,确保包含 `/plan`(见核心结论表);
2. 常见出错位置:Kimi Code 自定义 Provider、Claude Code `~/.claude/settings.json` 的 `ANTHROPIC_BASE_URL`、cc-switch 供应商"请求地址"、自研脚本直接抄了普通方舟文档的 `/api/v3`;
3. 注意配置优先级:环境变量可能覆盖配置文件,改完确认实际生效的值;
4. 让客户端重发一次请求验证 200。

## 一键诊断脚本

```bash
bash scripts/ark401-fingerprint.sh <ark-api-key> [model]
```

对给定 Key 跑 5 组对照实验(正确路径 / 错误路径 / 无认证头 / 缺 Bearer / 伪造 Key),输出 HTTP 码 + 服务端报错文案,末尾附判读指南。Key 全程打码显示。可用环境变量 `ARK_REGION` 切换区域(默认 `cn-beijing`)。

## 扩展排查项

- **arkcli SSO 过期 ≠ API Key 失效**:`arkcli auth status` 报 `refresh_token is invalid` 只影响 CLI 管理面(plans 查询 / 轮换 Key),不影响 Key 调用;重登 `arkcli auth login volc-sso` 即可;
- **模型别名属正常**:请求 `claude-sonnet-4-5` 由 `doubao-seed-*` 应答是 Agent Plan 的路由行为,不是错误;
- **Alibaba DashScope 401**(`Invalid API-key provided`,Request id 形如 `ba736c13-…`):含义是 Key 字符串本身被拒(错 Key / 截断 / 已重置),与套餐到期无关;去[百炼控制台](https://bailian.console.aliyun.com/) API-KEY 管理重建。

## 安全红线

- 任何输出(log / 报告 / 提交信息)中,Key 只显示前 8 位 + 后 6 位;
- 不要把用户的 Key 写进仓库、文档或 issue;
- 需要贴配置排查时,先让用户脱敏。
