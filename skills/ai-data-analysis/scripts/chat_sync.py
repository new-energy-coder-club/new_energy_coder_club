#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步调用音乐人智能数据分析接口 (DataAgentController#chatSync)

接口地址: https://y.tencentmusic.com/openapi/v1/musician/data/agent/chat-sync
请求方式: POST
Content-Type: application/json
认证方式: Header `tme-header-token: <TOKEN>`
         —— 网关会根据 Token 自动解析出 accountId 并注入 `X-Account-Id`，
            因此本脚本**不需要**也**不应该**再传 accountId。

登录态依赖（重要）:
  本脚本的 Token 来源依赖 `tme-openapi` skill 内嵌的登录能力。
  tme-openapi 通过 `scripts/_token.get_tme_header_token()` 对外暴露标准获取接口，
  内部维护的缓存文件为：
      ~/.tme-login/token.json  （字段 `token`，与 tme-openapi 共享）

  Token 读取优先级（从高到低）：
      1. 环境变量 TME_HEADER_TOKEN（兼容旧调用方式 / 显式覆盖场景）
      2. 调用 tme-openapi 的 _token.get_tme_header_token()
         （内部自动走：本地缓存 → 无头刷新 → 有头扫码 → 手动粘贴 四级回退）
      3. 直接读 ~/.tme-login/token.json 兜底（tme-openapi 不可用时）
      4. 以上都没有 → 报错并引导用户执行 tme-openapi 的 check_login.py

  ⚠️ 本脚本不再自行管理 Token 缓存，也不再依赖 tme-login skill。

用法:
  python chat_sync.py <userMessage> [songId]

示例:
  python chat_sync.py "我最近7天的播放量怎么样？"
  python chat_sync.py "分析这首歌最近的表现" 987654

说明:
  - userMessage 必填（字符串，用户的原始自然语言提问）
  - songId 可选（整数，仅当用户明确指向某首歌时传入）
  - accountId 由网关通过 tme-header-token 自动解析，**严禁**脚本再传
  - 接口内部同步等待 ChatBI 完整响应，正常耗时 20~90 秒，偶发可达 3 分钟
  - 脚本超时设置为 260 秒，略大于服务端 240 秒超时

返回:
  stdout 打印接口原始 JSON 响应（已格式化，便于调试）
  失败时 exit code 非 0
"""
import sys
import os
import json
import urllib.request
import urllib.error
from pathlib import Path


BASE_URL = os.environ.get("MUSICIAN_BASE_URL", "https://y.tencentmusic.com/openapi")
CHAT_SYNC_PATH = "/v1/musician/data/agent/chat-sync"

# 服务端内部超时 240s，脚本留 20s 缓冲
HTTP_TIMEOUT_SECONDS = 260

# tme-openapi skill 维护的 Token 缓存文件（与 tme-openapi 的 check_login.py 约定一致）
TME_LOGIN_TOKEN_FILE = Path.home() / ".tme-login" / "token.json"

# tme-openapi skill 目录（用于 import _token 模块 / 调起 check_login.py 兜底）
# 当前文件：<repo>/musician-claw/sit/ai-data-analysis/scripts/chat_sync.py
# tme-openapi：<repo>/musician-claw/sit/tme-openapi/scripts
_SIT_DIR = Path(__file__).resolve().parent.parent.parent
TME_OPENAPI_SCRIPTS_DIR = _SIT_DIR / "tme-openapi" / "scripts"


def load_token_via_tme_openapi() -> str:
    """优先调用 tme-openapi 的 _token.get_tme_header_token() 拿 Token

    该函数内部由 tme-openapi 的 check_login.py 完成四级回退：
        缓存 → 无头刷新 → 有头扫码 → 手动粘贴
    获取到的 Token 会被 tme-openapi 写入 ~/.tme-login/token.json，本脚本后续也能读到。

    失败（tme-openapi 不可用 / 用户中途放弃登录）时返回空串。
    """
    if not TME_OPENAPI_SCRIPTS_DIR.is_dir():
        return ""
    try:
        # 把 tme-openapi/scripts 临时加入 sys.path 以便 import _token
        if str(TME_OPENAPI_SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(TME_OPENAPI_SCRIPTS_DIR))
        import _token as _tme_openapi_token  # type: ignore
        token = _tme_openapi_token.get_tme_header_token(allow_interactive=True)
        return (token or "").strip()
    except Exception as e:
        # 常见情况：check_login.py 返回非零、用户放弃扫码、Playwright 未安装等
        print(f"⚠️ 通过 tme-openapi 获取 Token 失败: {e}", file=sys.stderr)
        return ""


def load_token_from_cache_file() -> str:
    """直接读 ~/.tme-login/token.json 兜底（tme-openapi 目录不可用时）

    文件格式（由 tme-openapi 的 check_login.py 写入）：
        {
            "token": "<tmeHeaderToken>",
            "savedAt": 1700000000,
            "baseUrl": "https://y.tencentmusic.com"
        }

    读不到或为空返回空字符串。
    """
    try:
        if not TME_LOGIN_TOKEN_FILE.exists():
            return ""
        with open(TME_LOGIN_TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return (data.get("token") or "").strip()
    except Exception:
        return ""


def resolve_token() -> str:
    """按优先级解析登录态 Token

    1. 环境变量 TME_HEADER_TOKEN（显式覆盖，最高优先级）
    2. 调用 tme-openapi 的 _token.get_tme_header_token()
       （内部自动走：缓存 → 无头刷新 → 有头扫码 → 手动粘贴 四级回退）
    3. 直接读 ~/.tme-login/token.json 兜底（tme-openapi 不可用时）
    4. 以上都没有 → 返回空串，由调用方负责报错引导
    """
    env_token = (os.environ.get("TME_HEADER_TOKEN") or "").strip()
    if env_token:
        return env_token

    openapi_token = load_token_via_tme_openapi()
    if openapi_token:
        return openapi_token

    file_token = load_token_from_cache_file()
    if file_token:
        return file_token

    return ""


def main():
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <userMessage> [songId]", file=sys.stderr)
        sys.exit(1)

    # 入参解析
    user_message = sys.argv[1]
    if not user_message or not user_message.strip():
        print("❌ userMessage 不能为空", file=sys.stderr)
        sys.exit(1)

    song_id = None
    if len(sys.argv) >= 3 and sys.argv[2].strip():
        try:
            song_id = int(sys.argv[2])
        except ValueError:
            print(f"❌ songId 必须是整数，当前值: {sys.argv[2]}", file=sys.stderr)
            sys.exit(1)

    # 认证：仅支持登录态 Token
    # 网关会根据 tme-header-token 自动解析出当前用户的 accountId 并透传给后端
    tme_header_token = resolve_token()
    if not tme_header_token:
        print("❌ 未获取到登录态 Token", file=sys.stderr)
        print(
            "   已尝试来源：环境变量 TME_HEADER_TOKEN、"
            f"tme-openapi({TME_OPENAPI_SCRIPTS_DIR})、{TME_LOGIN_TOKEN_FILE}",
            file=sys.stderr,
        )
        print(
            "   请先通过 tme-openapi skill 完成登录（例如执行其 scripts/check_login.py），",
            file=sys.stderr,
        )
        print(
            "   或者在本 skill 目录下执行 `python3 scripts/check_login.py` 触发登录流程。",
            file=sys.stderr,
        )
        sys.exit(1)

    # 请求体：只需 userMessage，以及可选 songId
    body = {
        "userMessage": user_message,
    }
    if song_id is not None:
        body["songId"] = song_id

    url = f"{BASE_URL}{CHAT_SYNC_PATH}"
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("tme-header-token", tme_header_token)

    print(f"📡 POST {url}", file=sys.stderr)
    print(f"⏳ 数据分析通常需要 20~90 秒，请耐心等待...", file=sys.stderr)

    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8")
        result = json.loads(raw)
        print(json.dumps(result, indent=4, ensure_ascii=False))

        # 基础业务码校验
        if isinstance(result, dict) and result.get("code") not in (0, None):
            print(f"⚠️ 接口返回非成功码: code={result.get('code')}, message={result.get('message')}",
                  file=sys.stderr)
            sys.exit(2)
        sys.exit(0)
    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        print(f"❌ HTTP 错误 {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ 网络请求失败: {e}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print(f"❌ 请求超时（{HTTP_TIMEOUT_SECONDS}s），数据分析耗时较长，请稍后再试", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
