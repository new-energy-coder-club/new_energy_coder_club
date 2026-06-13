#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 `tme-openapi` skill 获取登录态 Token（本 skill 不再自带登录逻辑）

依赖关系：
    本脚本是 `tme-openapi` skill 的薄封装，所有登录态的生成 / 刷新 / 扫码
    都由 `tme-openapi` 负责。本脚本只做两件事：
      1. 优先调用 tme-openapi 提供的 Python API:
         `from tme_openapi_scripts._token import get_tme_header_token`
         （路径：<repo>/musician-claw/sit/tme-openapi/scripts/_token.py）
      2. 若 import 失败（例如运行环境不同），回退到子进程调起
         `tme-openapi/scripts/check_login.py`，由它走
         「缓存 → 无头刷新 → 扫码登录 → 手动粘贴」四级回退链。

    tme-openapi 与 tme-login 共用同一个本地缓存文件 `~/.tme-login/token.json`，
    所以历史 Token 缓存对本次迁移完全兼容，不需要重新登录。

用法:
    python3 check_login.py              # 默认：走 tme-openapi 完整获取链
    python3 check_login.py --no-login   # 只读缓存 + 无头刷新，不触发有头扫码
    python3 check_login.py --force      # 忽略本地缓存，强制刷新

输出:
    成功: stdout 输出 `export TME_HEADER_TOKEN="..."` 命令，
          可通过 `eval $(python3 check_login.py)` 一步更新环境变量；
    失败: exit code 1，提示信息写 stderr。

注意:
    - 不再接受 Token 位置参数；如需手动粘贴 Token，请走
      `python3 <tme-openapi>/scripts/check_login.py --manual`。
    - 不再维护 `~/.musician/token` 缓存，Token 的唯一可信来源是
      tme-openapi 维护的 `~/.tme-login/token.json`。
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# ---- tme-openapi 依赖定位 ----
# 当前文件位于：<repo>/musician-claw/sit/ai-data-analysis/scripts/check_login.py
# tme-openapi 位于：<repo>/musician-claw/sit/tme-openapi
SCRIPT_DIR = Path(__file__).resolve().parent
TME_OPENAPI_DIR = (SCRIPT_DIR.parent.parent / "tme-openapi").resolve()
TME_OPENAPI_SCRIPTS_DIR = TME_OPENAPI_DIR / "scripts"
TME_OPENAPI_CHECK = TME_OPENAPI_SCRIPTS_DIR / "check_login.py"


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _try_inprocess_get_token(allow_interactive: bool) -> str:
    """优先以 Python API 方式调用 tme-openapi 的 _token.get_tme_header_token()

    成功 → 返回 token 字符串
    失败（模块不可用 / 调用报错）→ 返回空字符串，由调用方回退到子进程方式
    """
    try:
        if str(TME_OPENAPI_SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(TME_OPENAPI_SCRIPTS_DIR))
        # pylint: disable=import-outside-toplevel
        from _token import get_tme_header_token  # type: ignore
    except Exception as e:
        _eprint(f"⚠️ 无法 import tme-openapi._token 模块，回退到子进程方式: {e}")
        return ""

    try:
        token = get_tme_header_token(allow_interactive=allow_interactive)
        return (token or "").strip()
    except Exception as e:
        _eprint(f"⚠️ tme-openapi._token.get_tme_header_token 调用失败: {e}")
        return ""


def _fallback_subprocess(args_list) -> int:
    """回退方案：直接调起 tme-openapi/scripts/check_login.py
    该子脚本成功时 stdout 最后一行即为 token 本体。
    """
    if not TME_OPENAPI_CHECK.exists():
        _eprint("")
        _eprint("━" * 60)
        _eprint("❌ 未找到 tme-openapi skill 的 check_login.py")
        _eprint(f"   期望路径: {TME_OPENAPI_CHECK}")
        _eprint("   请确认 tme-openapi skill 已与本 skill 同级部署。")
        _eprint("━" * 60)
        return 1

    cmd = [sys.executable, str(TME_OPENAPI_CHECK)] + list(args_list)
    _eprint(f"🔗 调起 tme-openapi 登录流程: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, text=True)
    except Exception as e:
        _eprint(f"❌ 调用 tme-openapi/check_login.py 失败: {e}")
        return 1

    if result.returncode != 0:
        return result.returncode

    out = (result.stdout or "").strip()
    if not out:
        _eprint("❌ tme-openapi/check_login.py 未返回 Token")
        return 1

    token = out.splitlines()[-1].strip()
    if not token:
        _eprint("❌ tme-openapi/check_login.py 返回空 Token")
        return 1

    emit_export(token)
    return 0


def emit_export(token: str) -> None:
    """stdout 输出 export 命令，方便 eval $(...) 使用"""
    os.environ["TME_HEADER_TOKEN"] = token
    _eprint("✅ 已从 tme-openapi 获取有效 Token")
    _eprint("🔄 请执行以下命令更新环境变量：")
    _eprint(f'   export TME_HEADER_TOKEN="{token}"')
    print(f'export TME_HEADER_TOKEN="{token}"')


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 tme-openapi skill 获取登录态 Token（本 skill 不再自带登录逻辑）"
    )
    parser.add_argument("--no-login", action="store_true",
                        help="只读缓存 + 无头刷新，不触发 tme-openapi 的有头扫码")
    parser.add_argument("--force", action="store_true",
                        help="忽略本地缓存，强制让 tme-openapi 刷新 Token")
    args = parser.parse_args()

    # 方式 A（优先）：以 Python API 方式调用 tme-openapi._token.get_tme_header_token
    # --force 走子进程方式以支持 --force 参数透传
    if not args.force:
        allow_interactive = not args.no_login
        token = _try_inprocess_get_token(allow_interactive=allow_interactive)
        if token:
            emit_export(token)
            return 0
        _eprint("↩️ in-process 方式未拿到 Token，回退到子进程方式")

    # 方式 B（回退）：子进程调起 tme-openapi/scripts/check_login.py
    extra = []
    if args.force:
        extra.append("--force")
    if args.no_login:
        extra.append("--no-login")
    return _fallback_subprocess(extra)


if __name__ == "__main__":
    sys.exit(main())