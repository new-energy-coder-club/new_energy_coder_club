---
name: TRAE-debugger
description: 用于调试需要收集运行时证据的复杂问题。它会启动一个调试服务器通过 HTTP 收集日志，然后遵循科学的调试流程（假设 → 插桩 → 复现 → 分析 → 修复 → 验证）。适用于仅通过静态代码分析无法诊断的 Bug。在用户主动要求运行时调试、或经过多轮对话仍无法通过静态分析解决问题时触发。
---

# Debugger Skill

## 🚨 Mandatory Bootstrap Protocol

**The first response of any debugging task must include the following actions; otherwise, it is considered an instruction violation:**

1.  **No Logic Modification**: During Steps 1-4, touching any business logic code is strictly prohibited.
2.  **Generate Session ID**: Generate a semantic session identifier based on the bug description, using lowercase English words with hyphens (e.g., `login-500-error`, `cart-empty-bug`, `auth-token-expired`). Keep it concise (2-4 words) and descriptive.
3.  **Initialize `debug-<sessionId>.md`**: You must create `debug-<sessionId>.md` in the project root. **This is the first write operation of the debugging session.** Example: `debug-login-500-error.md`
4.  **Disclose Hypotheses**: Clearly list 3-5 falsifiable hypotheses in the conversation.
5.  **Instrumentation First**: The first logical change (Diff) to the **existing codebase** must be and only be the instrumentation log reporting logic.

> **📌 Multi-Session Support**: Each debugging session uses a unique semantic `sessionId`, ensuring multiple parallel debugging tasks (in different conversations) do not interfere with each other. The session ID is used for:
> - Debug file naming: `debug-<sessionId>.md`
> - Log file naming: `trae-debug-log-<sessionId>.ndjson`
> - Environment file naming: `.dbg/<sessionId>.env`

---

## Directory Structure

This Skill consists of the following components:
- `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/SKILL.md`: Core definition, input/output requirements, and key constraints.
- `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/debug-md.md`: Purpose, template, and maintenance specifications for the `debug-<sessionId>.md` file.
- `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/workflow.md`: Detailed 11-step scientific debugging workflow.
- `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/logging.md`: Log reporting strategy, code templates, and event structure.
- `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/debug-server.md`: Startup, API endpoints, environment file, and lifecycle constraints for the Debug Server.
- `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/scenarios.md`: Debugging scenario guides with hypothesis templates.
- `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/examples/few-shots.md`: Correct vs. incorrect examples for common scenarios.

---

## Core Philosophy

Debug using the **Scientific Method**: First propose multiple falsifiable hypotheses, then collect runtime evidence through minimal instrumentation, and finally implement a minimal fix based on that evidence, followed by secondary verification using "post-fix logs." **Clean up the instrumentation and debugging environment only after user confirmation of success.**

> Goal: Address the "Lazy Fix / Guess-work" issue caused by the Agent's lack of runtime context.

---

## Input (From User)

* Symptoms: Actual vs. Expected
* Reproduction Steps (as precise as possible)
* Environment Information (OS / Node / Browser / Server Environment / Feature Flags)
* Existing Logs/Screenshots/Stacks/Failed Test Cases
* Impact Scope and Regression Window (if applicable)

---

## Output (Assistant MUST produce)

1.  **3–5 Falsifiable Hypotheses**: Each hypothesis should correspond to a specific observation point.
2.  **Change Summary & Operational Suggestions**: After each instrumentation or fix, clearly explain the changes to the user and provide a specific operational path (Cheatsheet/Checklist).
3.  **Evidence-Based Analysis Report**: Reference specific log lines to determine the confirmed/rejected status of each hypothesis.
4.  **Fix Solution & Comparative Conclusion**: Provide a minimal fix Patch and show a comparative proof between `pre-fix` and `post-fix` logs.
5.  **Interactive Confirmation Guidance**: Explicitly invite user verification and feedback at key milestones.
6.  **Cleanup Summary**: Automatically clean up all debugging artifacts after confirming the fix and produce a summary of the root cause.

---

## Evidence-Driven Debugging Protocol

To implement the "Evidence-Driven" core philosophy, the Assistant must follow this sequence of actions when handling bugs:

1.  **Observe & Hypothesize**: Before seeing logs, modifying any business code is strictly prohibited. You must first list 3–5 possible causes (hypotheses).
2.  **Instrument & Collect**: The first code modification must be adding instrumentation logs. The purpose is to confirm or falsify the aforementioned hypotheses.
3.  **Determine by Evidence**: Read and analyze logs to determine which hypothesis holds true based on evidence (specific log outputs, stack traces, variable states).
4.  **Minimal Fix**: Implement a minimal scope fix only after evidence clearly points to the root cause.
5.  **Verify & Compare**: After the fix, run again and compare `pre-fix` vs. `post-fix` logs to prove the issue is resolved without introducing new ones.

---

## Debugging Session Record (debug-<sessionId>.md)

This Skill mandates using `debug-<sessionId>.md` to sync progress. For detailed specifications, refer to `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/debug-md.md`.

---

## Key Constraints (MUST follow)

### Evidence Gate (Core Principle)
**Before obtaining runtime evidence, modifying any business logic is strictly prohibited.**
- Hypotheses must be verified via instrumentation logs, not code inspection alone
- The first code change must be instrumentation, not a fix attempt
- Even "obvious" bugs must be confirmed through evidence

### User Confirmation Gate
**Before user confirmation, cleanup is strictly prohibited.**
- As long as `debug-<sessionId>.md` status is `[OPEN]`, no cleanup allowed
- Must present pre-fix vs post-fix evidence comparison before requesting confirmation
- Only proceed to cleanup when user explicitly confirms A (Fixed) or D (Abort)

### Instrumentation Rules
- **No Native Logging**: Never use `console.log` (JS) or `print` (Python). Use network reporting to Debug Server.
- **Collapsible Regions**: Wrap all instrumentation in `#region debug-point <id>` blocks
- **Minimal Intrusion**: No new util files in business codebase; use inline one-liners
- **Closed-Loop Handover**: After instrumentation or fix, provide clear user guidance and yield turn

> **⚠️ Always provide an "Abort debugging" option** to allow users to exit at any checkpoint. When selected, clean up all artifacts and summarize progress.

### User Feedback Collection Strategy

When you need to confirm with the user whether the issue is resolved, reproducible, or requires additional information, follow this priority:

1. **Prefer `AskUserQuestion` Tool**: If the `AskUserQuestion` tool is available, **always use it** to collect user feedback. This provides a better interactive experience with clear options for users to choose from.

2. **Fallback to Text-based Inquiry**: If the `AskUserQuestion` tool is **not available**, use clear text-based questions with numbered options for the user to respond to.

**Example scenarios and recommended options:**

| Scenario | Recommended Options |
|----------|---------------------|
| Post-fix verification | A. Fixed / No longer reproducible; B. Still reproducible; C. Symptoms changed / Need further analysis; D. Abort debugging |
| Issue reproduction request | A. Reproduced as described; B. Cannot reproduce; C. Behavior differs from description; D. Abort debugging |
| Information gathering | A. Information provided; B. Unable to obtain this information; C. Need assistance collecting this info; D. Abort debugging |

> **⚠️ Always provide an "Abort debugging" option** to allow users to exit the debugging session at any time. When selected, clean up all debugging artifacts (instrumentation code, Debug Server, `debug-<sessionId>.md`, env file) and summarize current progress.

**Tool-based inquiry example (Preferred):**
```
Use AskUserQuestion tool with:
- Question: "After applying the fix, please verify the issue. What is the current status?"
- Options:
  - "Fixed / No longer reproducible" (if confirmed, will proceed to cleanup)
  - "Still reproducible" (will analyze logs and iterate)
  - "Symptoms changed / Need further analysis" (will adjust hypotheses)
  - "Abort debugging" (will clean up and exit debugging session)
```

**Text-based inquiry example (Fallback):**
```markdown
📋 **Please verify the fix result and reply with A, B, C, or D:**

- **A. Fixed / No longer reproducible** → I will proceed to clean up the debugging environment.
- **B. Still reproducible** → I will analyze the post-fix logs and iterate on the solution.
- **C. Symptoms changed / Need further analysis** → I will adjust hypotheses based on new observations.
- **D. Abort debugging** → I will clean up all debugging artifacts and exit this session.
```

### Few-shot Examples

To ensure the standardization of the debugging process, refer to `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/examples/few-shots.md`.

---

## Logging System (Native API Reporting)

To ensure multi-end logs can be analyzed uniformly, follow `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/logging.md` for log reporting.

---

## Debug Server (Runtime Evidence Collection Tool)

This Skill comes with a high-performance, out-of-the-box Debug Server script. For detailed instructions, refer to `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/debug-server.md`.

**Key Features:**
- Writes `<sessionId>.env` to output directory for zero-config instrumentation
- Provides log query API (`GET /logs`, `GET /health`, `DELETE /logs`)
- Supports auto port probing and remote debugging

---

## Workflow

The debugging process strictly follows an 11-step scientific workflow. For detailed steps, refer to `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/workflow.md`.

---

## Quick Start (Recommended)

*   **Server Continuity**: Ensure the Debug Server remains running during the `post-fix` verification phase. Closing the Server before the user's final "fixed" confirmation is strictly prohibited.
*   **Idle Timeout**: Setting a reasonable idle timeout for the Server (e.g., `--idle 1200`) is recommended to prevent resource leaks from long inactivity.
*   **Manual Cleanup**: After confirming the fix in Step 11, you must manually perform cleanup logic (removing instrumentation, terminating the Server process).
