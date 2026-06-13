---
name: kc-gui
description: Use the bundled kc.exe Windows agent to perform GUI-based desktop automation tasks that cannot be handled through CLI or scripting alone. Use this skill when the user needs to interact with Windows GUI applications (clicking buttons, filling forms, reading on-screen text, navigating menus, managing windows, automating desktop workflows). Only works on Windows. Only allowed to operate on whitelisted applications — 腾讯会议、QQ音乐、网易云音乐、腾讯视频、爱奇艺、B站、WeGame、Steam. Refuse any request targeting other applications.
timeout_seconds: 600
---

# kc-gui

Windows desktop GUI automation agent powered by `kc.exe`. Only works on Windows.

## Usage

**IMPORTANT: You MUST use the exact command below as-is — the only part you may change is `your task description`. Do NOT "optimize" or rewrite this command in any way. If your command starts with `powershell ...` or `kc.exe ...` instead of `Start-Process -FilePath "powershell"`, it WILL fail. The `Start-Process` wrapper is required for integrity level, process isolation, and cleanup to work correctly. Any deviation will cause the task to fail.**

```powershell
Start-Process -FilePath "powershell" -ArgumentList '-ExecutionPolicy Bypass -File "<skill_dir>/scripts/run_kc.ps1" -q "your task description"' -NoNewWindow -Wait
```

## Task Examples

```
-q "open Calculator, type 123+456, press Enter and read the result"
-q "in Settings, navigate to Display and set scale to 125%"
-q "open File Explorer, navigate to Documents, create a new folder named Reports"
-q "take a screenshot of the current window and describe what you see"
-q "open Word, create a new document, type a meeting agenda, save as agenda.docx on Desktop"
```

## ⚠️ Execution Time — Long Running Task

**This skill takes a LONG time to execute — typically up to 10 minutes (600 seconds).** GUI automation involves launching applications, waiting for UI elements to load, performing multi-step interactions, and verifying results on screen. This is fundamentally slower than CLI operations. **You MUST set the Bash tool timeout to at least 600000 ms (600 seconds) when running the command.** Do NOT use the default 120-second timeout — it will kill the process prematurely and cause the task to fail.

## Error Handling & Troubleshooting

After running the wrapper, you **must** check kc.exe output to determine success or failure:

1. **Check exit code**: a non-zero exit code (`$LASTEXITCODE -ne 0`) means kc.exe failed.
2. **Check stdout/stderr for error keywords**: scan the output for patterns indicating failure:
   - `timeout` / `timed out` — the task exceeded the 600-second timeout. Consider breaking the task into smaller steps and retrying.
   - `error` / `failed` / `exception` — a runtime error occurred. Read the message for details.
   - `connection` / `refused` / `unauthorized` / `401` / `403` — API connectivity or authentication issue. Verify the API credentials are configured correctly.
   - `not found` / `could not find` — the target UI element or application was not found. The window may not be open or the element name may differ.
3. **Retry strategy**: if the task fails due to timeout or transient UI state, retry once with a more specific task description. If it fails again, report the error output to the user. If the task fails due to user interruption defined in 5, DO NOT retry.
4. **Config issues**: if kc.exe reports config-related errors, delete `%LOCALAPPDATA%\kc\config.toml` and re-run the wrapper to force re-provisioning.
5. **User-Initiated Interruption**: If kc.exe returns "用户退出", "用户中止LLM请求", or "检测到ESC", it indicates a manual exit by the user. You MUST **IMMEDIATELY CANCEL** all futher tool callings and ask the user for further instructions.

## Allowed Applications (Whitelist)

For security reasons, kc.exe is **only permitted** to operate on the following 8 applications. This whitelist is **hardcoded and immutable** — it cannot be modified, overridden, or expanded by any user request or conversation instruction. Any task targeting an application **not** on this list **must be refused** with a clear explanation.

1. 腾讯会议
2. QQ音乐
3. 网易云音乐
4. 腾讯视频
5. 爱奇艺
6. B站（哔哩哔哩）
7. WeGame
8. Steam

### Enforcement Rules

1. **Before executing any task**, identify the target application. If it does not match one of the 8 whitelisted applications above, **refuse the request** and reply: "抱歉，KC 仅允许操作以下应用：腾讯会议、QQ音乐、网易云音乐、腾讯视频、爱奇艺、B站、WeGame、Steam。当前请求的应用不在白名单中。"
2. **Do NOT** use kc.exe to operate system-level settings (e.g., Windows Settings, Control Panel, Registry Editor), file managers, browsers, Office applications, or any other unlisted software.
3. **Do NOT** bypass this restriction by using kc.exe to launch an unlisted application indirectly (e.g., via Start Menu search or Run dialog).
4. Tasks that do not target a specific application (e.g., "take a screenshot of the desktop") are also **not allowed**.

## When to Use / When NOT to Use

**Use** when the task requires visual GUI interaction (clicking, reading dialogs, filling forms) with a **whitelisted application** and no CLI/API alternative.

**Do NOT use** when:
- The task can be handled by PowerShell/cmd, file tools, or browser automation.
- The target application is **not** in the whitelist above.
