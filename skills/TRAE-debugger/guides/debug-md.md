## Debugging Session Record (debug-<sessionId>.md)

This file is the single source of truth for debugging progress. Created in project root at session start.

> **📌 Naming**: Use semantic identifiers like `login-500-error`, `cart-empty-bug`

### Purpose
- **Status Tracking**: `[OPEN]` / `[FIXED]`
- **Evidence Chain**: Hypotheses, log evidence, verification conclusions
- **Cleanup Gate**: No cleanup while status is `[OPEN]`

### File Template

```markdown
# Debug Session: [sessionId]
- **Status**: [OPEN] / [FIXED]
- **Issue**: Brief description
- **Debug Server**: http://127.0.0.1:<port>/event
- **Log File**: .dbg/trae-debug-log-<sessionId>.ndjson

## Reproduction Steps
1. ...

## Hypotheses & Verification
| ID | Hypothesis | Likelihood | Effort | Evidence |
|----|------------|------------|--------|----------|
| A | ... | High/Med/Low | Low/Med/High | Pending/Confirmed/Rejected |

## Log Evidence
[Key log entries]

## Verification Conclusion
[Pre-fix vs post-fix comparison]
```

### Lifecycle
1. **Create** at Step 1 (before any code changes)
2. **Update** after instrumentation, log analysis, and fix attempts
3. **Close** only after user confirms fix (change status to `[FIXED]`)
4. **Delete** after final cleanup completes
