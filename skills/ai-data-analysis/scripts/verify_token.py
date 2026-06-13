#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 tme-header-token 是否有效（跨平台）

⚠️ 登录态管理已委托给 `tme-openapi` Skill，本脚本优先把校验请求转发给
   `tme-openapi/scripts/verify_token.py`；若 tme-openapi 目录不可用（用户未安装该
   Skill），则回退到本地最小实现，保证即使单独部署也能正常工作。

用法: python verify_token.py <token>
返回: 成功输出用户信息 JSON，失败返回 exit code 1
"""
import sys
import os
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# ai-data-analysis/scripts/verify_token.py → 向上两级是 sit/，再定位到 tme-openapi
SIT_DIR = Path(__file__).resolve().parent.parent.parent
TME_OPENAPI_VERIFY = SIT_DIR / "tme-openapi" / "scripts" / "verify_token.py"


def delegate_to_tme_openapi(token: str) -> int:
    """把校验转发给 tme-openapi/scripts/verify_token.py，返回其 exit code；
    若 tme-openapi 不存在则返回 -1 表示需要回退。"""
    if not TME_OPENAPI_VERIFY.is_file():
        return -1
    try:
        result = subprocess.run(
            [sys.executable, str(TME_OPENAPI_VERIFY), token],
            check=False,
        )
        return result.returncode
    except Exception as e:
        print(f"⚠️ 调用 tme-openapi/verify_token.py 失败，回退本地实现: {e}",
              file=sys.stderr)
        return -1


def verify_locally(token: str) -> int:
    """本地最小实现：直接请求 userInfo 接口，兼容 tme-openapi 未安装的场景。"""
    base_url = os.environ.get("MUSICIAN_BASE_URL", "https://y.tencentmusic.com")
    url = f"{base_url}/v2/v2/account/userInfo"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    req.add_header("tme-header-token", token)

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("ret") == 0 or data.get("code") == 0 or data.get("success") is True:
            print("✅ Token 有效")
            print(json.dumps(data, indent=4, ensure_ascii=False))
            return 0
        print("❌ Token 无效或已过期")
        return 1
    except urllib.error.HTTPError as e:
        print(f"❌ Token 验证失败，HTTP 错误 {e.code}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Token 验证请求失败: {e}", file=sys.stderr)
        return 1


def main():
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <tme-header-token>", file=sys.stderr)
        sys.exit(1)

    token = sys.argv[1]

    # 优先委托给 tme-openapi
    rc = delegate_to_tme_openapi(token)
    if rc != -1:
        sys.exit(rc)

    # 回退本地实现
    sys.exit(verify_locally(token))


if __name__ == "__main__":
    main()
