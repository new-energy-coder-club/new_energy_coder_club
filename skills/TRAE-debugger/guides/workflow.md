## Workflow

### Step 1 — Problem Definition & Initialization (BLOCKING)

1.  **Restate the Issue**: Clearly define the difference between actual behavior and expected behavior.
2.  **Generate Session ID**: Create a semantic session identifier based on the bug description using lowercase English words with hyphens (e.g., `login-500-error`, `cart-empty-bug`).
3.  **Create debug-<sessionId>.md**: Initialize `debug-<sessionId>.md` in the project root, recording the initial status `[OPEN]`, problem description, and known reproduction steps.

> **⚠️ Core Constraint**: Modifying any business logic code is strictly prohibited during this phase. **Executing any other write operations before creating `debug-<sessionId>.md` is strictly forbidden.**

> **💡 User Guidance**: After this step, inform the user:
> - The session ID being used (e.g., `login-500-error`)
> - Where the debug file is located (e.g., `debug-login-500-error.md`)
> - What the next steps will be

Output: Bug Brief + `debug-<sessionId>.md` (Initial)

---

### Step 2 — Hypothesis Generation (3–5 items) (BLOCKING)

Generate hypotheses with **Likelihood** and **Effort** assessment to prioritize verification:

| ID | Hypothesis | Likelihood | Effort | Expected Signal |
|----|------------|------------|--------|-----------------|
| A | Description | High/Medium/Low | Low/Medium/High | What logs would confirm |

**Prioritization Rule**: Verify **High Likelihood + Low Effort** hypotheses first.

Each hypothesis must include:

*   What signals will be seen in the logs if true (falsifiable signals).
*   Where instrumentation is needed (minimal points).
*   Whether it can be determined by a single fastest reproduction.

**Example**:
| ID | Hypothesis | Likelihood | Effort | Expected Signal |
|----|------------|------------|--------|-----------------|
| A | Database connection timeout | High | Low | `ETIMEDOUT` in error object |
| B | Auth token expired | Medium | Low | `401` response code |
| C | Memory leak causing slowdown | Low | High | Memory growth pattern over time |

> **💡 Tip**: Start with Hypothesis A (High likelihood, Low effort). Refer to `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/guides/scenarios.md` for scenario-specific hypothesis templates.

Output: Hypothesis Table (A–E) with Likelihood/Effort

---

### Step 3 — Instrumentation Design (3–8 points)

Principle: Use the minimum amount of logs to simultaneously distinguish 3–5 hypotheses (parallel verification).

Requirements:

*   Each log must be bound to a `hypothesisId`.
*   Instrumentation code must use semantic tags: `// #region debug-point <hypothesisId>[:description]`.
*   It is recommended to include a unified log prefix in the `message` field (default `[DEBUG]`).

Output: List of Insertion Points + Expected Signals

---

### Step 4 — Instrumentation Patch (No Behavioral Changes)

*   **Strictly Prohibit Business Logic Changes**: Code changes in this step are limited only to adding instrumentation logs; fixing any discovered potential bugs or performing refactoring is forbidden.
*   **Strictly Prohibit Creating New Util Files**: Use inline one-liners or reuse existing capabilities.
*   Introduce lightweight inline reporting logic (One-liner).

> **💡 User Guidance**: After instrumentation, clearly explain to the user:
> - Which files were modified and why
> - The instrumentation code uses the env file for configuration (no manual setup needed)
> - What to do if the env file cannot be read (fallback URL)

Output: Instrumentation Diff

---

### Step 5 — Log Initialization (MANDATORY)

*   **Clear Content**: If log files related to the current `sessionId` already exist in the `.dbg/` directory, clear their contents (do not delete the files).
*   **Confirm Status**: Ensure `runId = "pre-fix"`.

Output: Reproduction Steps (must include runId/sessionId)

---

### Step 6 — Interactive Reproduction (User Participation)

1.  **Clear Logs (MANDATORY)**: Before formally inviting the user to operate, **the contents of the current Session's log files must be cleared** to ensure the collected evidence contains only data from the current run, avoiding confusion with old logs.
2.  **Summarize Current Changes**: Clearly explain to the user which instrumentation points were
 added and their purpose.
3.  **Provide Operational Suggestions**: Give specific reproduction paths or a Checklist.
4.  **Invite User Action**: Request the user to perform the reproduction and provide log snippets or paths.

Output: Evidence (Runtime Logs)

---

### Step 7 — Evidence-Based Analysis

> **⚠️ Log Reading Constraint**: Read logs directly from `.dbg/trae-debug-log-<sessionId>.ndjson` using file read tool. **Do NOT use `curl` or HTTP API** (e.g., `curl -s "http://127.0.0.1:7777/logs" | head`) to query logs.

1.  **Read Evidence**: Use file read tool to read `.dbg/trae-debug-log-<sessionId>.ndjson` and extract relevant log entries.
2.  **Determine Hypotheses**: Mark each hypothesis as CONFIRMED / REJECTED / INCONCLUSIVE.
3.  **Present Verification Status**: Report hypothesis verification status to user in table format:

| ID | Hypothesis | Status | Evidence Summary |
|----|------------|--------|------------------|
| A | Database connection timeout | ✅ Confirmed | Line 23: `ETIMEDOUT` in error object |
| B | Auth token expired | ❌ Rejected | Line 45: Token valid, 200 response |
| C | Memory leak | ⏳ Inconclusive | Insufficient data for pattern analysis |

4.  **Update Records**: Synchronize these verification conclusions in `debug-<sessionId>.md`, referencing specific log lines.

> **💡 User Guidance**: When presenting verification results:
> - Use the table format above to clearly show confirmed/rejected/inconclusive hypotheses
> - Provide brief evidence summary for each hypothesis
> - Highlight the confirmed root cause if identified

Output: Root cause + Verification Table + `debug-<sessionId>.md` (Updated)

---

### Step 8 — Minimal Fix (Retain Instrumentation)

1.  Implement a minimal fix Patch.
2.  Summarize the fix logic for the user and explain why instrumentation is retained for comparative verification.

---

### Step 9 — Post-Fix Verification (Interactive Feedback)

1.  **Clear Logs (MANDATORY)**: Before guiding the user through fix verification, **previous debugging logs must be cleared** to ensure the post-fix evidence is pure.
2.  **Update runId**: Set `runId="post-fix"`.
3.  **Guide Verification**: Provide the suggested operational path after the fix and guide the user to interact again.
4.  **No Premature Cleanup**: All instrumentation and the Debug Server must be retained at this point so that evidence collection can immediately continue if the user reports "not fixed."
5.  **Collect User Feedback**: **MUST use `AskUserQuestion` tool** to ask whether the problem is solved (see Step 10 for options).

---

### Step 10 — User Confirmation Gate (Sole Cleanup Entry)

> **⚠️ MANDATORY: Use `AskUserQuestion` Tool**
>
> You **MUST** use the `AskUserQuestion` tool to collect user feedback. **Do NOT** present text-based A/B/C options like:
> ```
> ❌ WRONG - Do NOT do this:
> 请选择：
> A. 已修复
> B. 仍可复现
> C. 症状改变
> ```
> Instead, use `AskUserQuestion` with structured options.

**Cleanup logic in Step 11 can only and must be executed when the user replies with A or D.**
*   **A. Fixed / No longer reproducible** -> Proceed to cleanup (with success summary).
*   **B. Still reproducible** -> Enter iteration.
*   **C. Symptoms changed / Further analysis needed** -> Enter iteration.
*   **D. Abort debugging** -> Proceed to cleanup (with progress summary, no fix applied).

**AskUserQuestion Example:**
```json
{
  "question": "Is the issue resolved after the fix?",
  "header": "Verify Fix",
  "options": [
    { "label": "Fixed", "description": "Issue is resolved, proceed to cleanup" },
    { "label": "Still reproducible", "description": "Issue persists, continue investigation" },
    { "label": "Symptoms changed", "description": "Different behavior observed, needs analysis" },
    { "label": "Abort debugging", "description": "Stop debugging and cleanup" }
  ]
}
```

> **💡 User Guidance**: When asking for confirmation, remind the user:
> - What verification steps to perform
> - Where to find the log file for reference

---

### Step 11 — Branching Decision

**If A (Fixed): Enter Cleanup & Summary Phase**
1.  **Update Status**: Change Status to `[FIXED]` in `debug-<sessionId>.md` and invite the user for a final confirmation.
2.  **Status Check & Cleanup**:
    *   Check Debug Server process status (e.g., `lsof -i :<port>`).
    *   If still running, explicitly terminate and exit the process.
    *   Completely remove all instrumentation code (code blocks marked with `#region debug-point`).
3.  **Delete All Debug Files (MANDATORY)**:

> **⚠️ MANDATORY: Delete All Debug Files**
>
> You **MUST** delete ALL of the following files. **Do NOT "archive" or "preserve" any debug files.**
> ```
> ❌ WRONG - Do NOT do this:
> 📁 调试文件归档
> - 日志文件：.dbg/xxx.ndjson（已保留）
> - 环境配置：.dbg/xxx.env（已保留）
> ```

**Files to DELETE:**
| File | Path Pattern |
|------|--------------|
| Debug record | `debug-<sessionId>.md` |
| Log file | `.dbg/trae-debug-log-<sessionId>.ndjson` |
| Env file | `.dbg/<sessionId>.env` |

4.  **Final Summary**: Summarize the problem principles based on evidence and complete the formal submission with minimal changes.

> **💡 User Guidance**: After cleanup, provide a summary including:
> - Root cause of the issue
> - What was fixed
> - Files that were **deleted** (not archived)

**If B or C (Not Fixed / Analysis Needed): Enter Iteration Loop**
1.  **Record Status**: Record in `debug-<sessionId>.md` why it wasn't fixed and update reproduction steps or hypotheses.
2.  **Status Check & Recovery**:
    *   Check if the Debug Server is still running. If it has exited due to timeout (idle), restart the Server.
    *   In-depth Analysis: Compare log differences between `pre-fix` and `post-fix`.
    *   Adjust Instrumentation: Adjust or add instrumentation points based on new findings, invite the user to continue interacting, and return to Step 5.

**If D (Abort): Enter Cleanup Phase**
1.  **Record Status**: Record in `debug-<sessionId>.md` that debugging was aborted by user.
2.  **Cleanup (MANDATORY)** - Delete ALL debug files:
    *   Completely remove all instrumentation code.
    *   Stop the Debug Server if running.
    *   **DELETE**: `.dbg/trae-debug-log-<sessionId>.ndjson`
    *   **DELETE**: `.dbg/<sessionId>.env`
    *   **DELETE**: `debug-<sessionId>.md`
3.  **Summary**: Provide a brief summary of what was investigated and current findings (even if inconclusive).
