## Few-shot Examples

### 1. Evidence First, No Blind Fixing

**❌ Bad:**
> User: Clicking the submit button has no response.
> Assistant: I guess the `onClick` is not bound. Let me fix it for you.

**✅ Good:**
> User: Clicking the submit button has no response.
> Assistant: I'll investigate with hypotheses:
> 1. Event not triggered (DOM selector issue)
> 2. Handler throws error
> 3. API call fails
> 
> Let me add instrumentation first to determine which is true.

---

### 2. Mandatory Bootstrap Protocol

**❌ Bad:**
> User: Login page shows 500 error.
> Assistant: Might be a DB timeout. Let me increase the timeout.

**✅ Good:**
> User: Login page shows 500 error.
> Assistant: Starting debug session `login-500-error`.
> Created `debug-login-500-error.md` to track progress.
> 
> Hypotheses:
> - A: DB credentials expired → Signal: `Access Denied`
> - B: Connection timeout → Signal: `ETIMEDOUT`
> - C: Pool exhaustion → Signal: `Pool Limit Reached`

---

### 3. User Confirmation Gate

**❌ Bad:**
> I confirmed the fix by comparing logs.
> I've cleaned up everything.
> *(Violation: Cleaned up without user confirmation)*

**✅ Good:**
> **Evidence Comparison:**
> - pre-fix: `auth_token` was `undefined`
> - post-fix: `auth_token` correctly loaded
> 
> `debug-auth-token-expired.md` remains `[OPEN]`.
> Please verify, then I'll clean up.

---

### 4. No Native Logging

**❌ Bad:**
```javascript
console.log("State:", state);
```

**✅ Good:**
```javascript
// #region debug-point A:state-check
fetch("http://127.0.0.1:7778/event", { method: "POST", body: JSON.stringify({ sessionId: "cart-bug", runId: "pre", hypothesisId: "A", msg: "[DEBUG] State", data: state }) }).catch(() => {});
// #endregion
```

---

### 5. User Feedback Collection

**❌ Bad:**
> Is it fixed now?

**✅ Good (with AskUserQuestion tool):**
> Question: "Please verify the fix. What is the status?"
> Options: Fixed / Still reproducible / Symptoms changed / Abort debugging

**✅ Good (text fallback):**
> Reply A/B/C/D:
> - **A. Fixed** → Will clean up
> - **B. Still reproducible** → Will iterate
> - **C. Symptoms changed** → Will adjust hypotheses
> - **D. Abort** → Will clean up and exit

---

### 6. Remote/Mobile Debugging

**❌ Bad:**
```javascript
fetch("http://127.0.0.1:7777/event", ...)  // Mobile can't access localhost
```

**✅ Good:**
> Started Debug Server in remote mode:
> ```bash
> python3 debug-server.py --remote --session mobile-crash
> ```
> Server at `http://192.168.1.5:7778/event`
> 
> ```javascript
> // #region debug-point A:init
> fetch("http://192.168.1.5:7778/event", { method: "POST", body: JSON.stringify({ sessionId: "mobile-crash", msg: "App init" }) });
> // #endregion
> ```
