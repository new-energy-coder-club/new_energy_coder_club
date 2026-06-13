# Log Collector (Debug Evidence Collector)

This directory contains two sets of high-performance, dependency-free Debug Server implementations. They are the core experimental tools of the Scientific Debug Loop Skill.

## Core Principle: Prefer Direct Use

**Rewriting these scripts during each debugging session is strictly prohibited.** They have been optimized to support CORS, automatic cleanup, and session isolation.

## Priority Rules (MUST follow)

1.  **Prefer Python Template** (`c:\Users\29711\.trae\builtin_skills\TRAE-debugger/tools/debug-server/python/debug-server.py`): Suitable for the vast majority of Unix/Linux/macOS environments.
2.  **Alternative Node Template** (`c:\Users\29711\.trae\builtin_skills\TRAE-debugger/tools/debug-server/node/debug-server.mjs`): Suitable for pure JS/TS development environments.
3.  **Environment Detection & Fallback**:
    *   Only when both of the above are unavailable is it permitted to detect the environment and refer to `c:\Users\29711\.trae\builtin_skills\TRAE-debugger/tools/debug-server/TEMPLATE.md` to quickly implement an equivalent tool.

## Log Reporting Constraints

- **NEVER use `console.log` or `print`**: Debugging logs must be uniformly reported to this server via HTTP POST.
- **Reason**: Native logs cannot be automatically collected and aggregated for analysis in asynchronous, distributed, or multi-end scenarios, which would lead to a break in the chain of evidence.
- **Form**: Must be reported in an inline one-liner form; introducing new util files is forbidden.

## Design Goals

- **Zero Dependencies**: Uses only Python/Node standard libraries.
- **Robustness**: Supports CORS and prevents lingering debug processes.
- **Temporality**: It is an experimental instrument, not business code.
