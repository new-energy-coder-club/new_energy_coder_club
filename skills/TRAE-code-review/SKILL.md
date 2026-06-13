---
name: TRAE-code-review
description: 用于执行代码审查任务。适用于审查合并请求、代码差异，并提供关于代码质量、正确性和最佳实践的结构化反馈。
---

### Basic Rules

- Always use **new-version line numbers** (i.e., line numbers from the new/right side of the diff) for issue locations.
- For multi-line issues, provide `[line_start, line_end]`; for single-line issues, both can be the same.

---

### Execution Steps

**Step 1: Determine Review Scope**
- If the user specifies a review scope (e.g., specific files, a merge request, or comparison with a specific branch), follow the user's requirements.
- If the user does not specify a scope, use the `AskUserQuestion` tool to ask the user for clarification before proceeding.
- Common scope scenarios:
  - "Review current changes" → Use `git diff` or workspace diff to get uncommitted changes.
  - "Review changes compared to branch X" → Use `git diff X` to get the diff.
  - "Review MR/PR #N" → Fetch the merge request diff using appropriate tools.
  - "Review file X" → Focus on the specified file's changes.

**Step 2: Context Gathering**
- You **MUST** call tools (such as `SearchCodebase`, `Read`) to fetch all relevant source and design evidence before commenting.

**Step 3: Infer Author's Intent**
- Analyze the provided code diff as a whole.
- Based on the patterns of changes (e.g., adding error handling, changing algorithms, refactoring variable names, modifying configuration), deduce the most probable intent of the author.
- Formulate this intent as a concise summary. For example:
  - "Intent: Refactoring the `calculate_total` function for better readability."
  - "Intent: Adding null checks to prevent potential `NullPointerException` in the `process_user` method."
  - "Intent: Fixing an off-by-one error in the pagination logic."
  - "Intent: Upgrading a dependency version and adapting the code to its new API."
- This inferred intent will serve as a critical context for the next steps.

**Step 4: Visual Summary with Mermaid Diagrams**
- **Always provide** at least one mermaid diagram to summarize the key changes.
- Determine the **number of diagrams** based on the scope of changes:
  - **1 diagram**: For simple or single-aspect changes (e.g., a bug fix, minor feature, changes in one module).
  - **2 diagrams**: For complex changes that span multiple aspects (e.g., both business logic and technical implementation changes, cross-module interactions, new features with multiple components).
- Generate mermaid diagrams to summarize the key changes:
  - **Business flow diagram**: Use `flowchart` or `sequenceDiagram` to illustrate the business logic changes (e.g., user workflow, data processing pipeline).
  - **Technical flow diagram**: Use `flowchart` or `sequenceDiagram` to show the technical changes (e.g., call sequences, data flow, request handling).
- **Diagram guidelines**:
  - **PREFER flowcharts and sequence diagrams** that show actual **logic chains, call sequences, or data flow**.
  - **AVOID static box diagrams** that only categorize or group changes without showing relationships or flow.
  - Use color blocks (`style` or `classDef`) to group related logic and highlight changed parts.
  - Keep diagrams concise — focus on **key changes only**, not the entire system.
  - Add brief annotations to explain the purpose of each section.
  - **Color Contrast Requirements** (IMPORTANT):
    - Always specify **both fill color AND text color** to ensure readability in both light and dark themes.
    - Use dark text (`color:#000` or `color:#1a1a1a`) on light backgrounds.
    - Use light text (`color:#fff` or `color:#f5f5f5`) on dark backgrounds.
    - Recommended high-contrast combinations:
      - ✅ `fill:#c8e6c9,color:#1a5e20` (light green bg + dark green text)
      - ✅ `fill:#bbdefb,color:#0d47a1` (light blue bg + dark blue text)
      - ✅ `fill:#fff3e0,color:#e65100` (light orange bg + dark orange text)
      - ✅ `fill:#f3e5f5,color:#7b1fa2` (light purple bg + dark purple text)
      - ❌ `fill:#c8e6c9` (missing text color — unreadable in dark theme!)
- **Bad example** (avoid this pattern — static boxes without flow):
  ```mermaid
  flowchart LR
      subgraph Category1["Debug Code"]
          A[console.log]
          B[TODO comment]
      end
      subgraph Category2["New Features"]
          C[/new route]
          D[Demo user fallback]
      end
  ```
- **Good example** (show actual logic flow):
  ```markdown
  📊 **Change Overview**

  **Business Flow Changes:**
  ```mermaid
  flowchart LR
      A[User Login] --> B{Has Token?}
      B -->|Yes| C[Validate Token]
      B -->|No| D[Redirect to Auth]
      C --> E[Load User Data]
      E --> F[Render Dashboard]
      style C fill:#c8e6c9,color:#1a5e20
      style E fill:#c8e6c9,color:#1a5e20
  ```

  **Technical Flow Changes:**
  ```mermaid
  sequenceDiagram
      participant Client
      participant API
      participant Cache
      participant DB
      Client->>API: POST /login
      API->>Cache: Check session
      Cache-->>API: Cache miss
      API->>DB: Query user
      DB-->>API: User data
      API->>Cache: Store session
      API-->>Client: 200 OK + token
  ```
  ```

**Step 5: Scan for Issues**
- Using the inferred intent from Step 3 as context, carefully analyze the code diff again.

**Step 5.5: Cross-Validation with Sub-Agents**
- Before presenting issues to the user, perform a **second-pass validation** to verify the existence and severity of each identified issue.
- **Validation Strategy**:
  1. **Parallel Verification**: Dispatch **2 sub-agents** in parallel. Each sub-agent independently validates **ALL X issues** found by the main agent.
  2. **Verification Focus**: Each validator should check every issue for:
     - **Existence**: Does the issue actually exist in the code? Is the line reference correct?
     - **Severity Assessment**: Is this a real problem (critical/major) or a minor/stylistic concern?
     - **False Positive Detection**: Could this be a false positive due to missing context?
  3. **Confidence Scoring**: Each issue receives a confidence score based on validator consensus:
     - ✅ **High Confidence** (2/2 validators agree the issue exists): Include in final report
     - ⚠️ **Medium Confidence** (1/2 validator confirms): Include with caveat
     - ❌ **Low Confidence** (0/2 confirm, both say false positive): Exclude from final report

- **Sub-Agent Dispatch Rules**:
  - Each sub-agent receives the **complete list of all X issues** to validate
  - Each sub-agent independently reads the relevant code context for every issue
  - Sub-agents work in parallel, unaware of each other's findings
  - Each sub-agent must return validation results for **ALL issues**:
    ```json
    [
      { "issue_id": 1, "exists": true, "severity": "major", "reasoning": "..." },
      { "issue_id": 2, "exists": false, "severity": "false_positive", "reasoning": "..." },
      ...
    ]
    ```

- **Validation Consolidation**:
  - Collect validation results from both sub-agents
  - For each issue, count how many validators confirmed it exists
  - Apply consensus-based confidence scoring:
    - 2/2 confirm → High Confidence → Include
    - 1/2 confirms → Medium Confidence → Include with note
    - 0/2 confirm → Low Confidence → Exclude
  - Document excluded issues with reasoning (for transparency, but do not present to user)

- **Fallback (Sub-Agent Not Available)**:
  - If sub-agents are not available, perform a self-review:
    1. Re-read each issue's code context with fresh perspective
    2. Challenge each finding: "Is this definitely a problem?"
    3. Remove any issue that cannot be confidently confirmed

**Step 6: Output Review Results**
- If **no issues** are found, output a brief summary stating that the code looks good (e.g., "✅ No issues found. The code changes look good.") and skip to the end.
- If issues are found, present the review results in a **table** with the following columns:
  | No. | Issue Title | Suggestion | Code Link |
  |-----|-------------|------------|-----------|
  | 1   | Title       | Suggestion | [file:line](file:///path/to/file#L123-L145) |
- The code link should use the standard markdown link format pointing to the file URI with line numbers.

**Step 7: Ask User for Fix Selection**
- After presenting the review table, ask the user which issues they want to fix.
- Follow the **User Interaction Strategy** below to collect user feedback.
- **Iterative Fix Loop**:
  - If the user selects "Fix All Issues" or specific issues to fix, proceed to fix them.
  - After completing the fixes, if there are remaining unfixed issues, present them again and use `AskUserQuestion` to ask the user for the next action.
  - Repeat until all issues are resolved.

---

### User Interaction Strategy

When you need to clarify review scope or ask the user which issues to fix, follow this priority:

1. **Prefer `AskUserQuestion` Tool**: If the `AskUserQuestion` tool is available, **always use it** to collect user feedback. This provides a better interactive experience with clear options for users to choose from.

2. **Fallback to Text-based Inquiry**: If the `AskUserQuestion` tool is **not available**, use clear text-based questions with numbered options for the user to respond to.

**Example scenarios and recommended options:**

| Scenario | Recommended Options |
|----------|---------------------|
| Clarify review scope | A. Review current workspace changes; B. Review changes compared to a specific branch; C. Review a specific MR/PR; D. Review specific files |
| Fix selection (after review) | A. Fix all issues; B. [Issue titles as multi-select options] |
| Remaining issues (after partial fix) | A. Fix all remaining issues; B. [Remaining issue titles as multi-select options] |

**Tool-based inquiry example for fix selection (Preferred):**
```
Use AskUserQuestion tool with:
- Question: "Which issues would you like me to fix?"
- Options (enable multi-select):
  - "Fix All Issues" (will fix all identified issues)
  - "[Issue Title 1]" (individual issue)
  - "[Issue Title 2]" (individual issue)
```

**Tool-based inquiry example for remaining issues (after partial fix):**
```
Use AskUserQuestion tool with:
- Question: "The following issues remain unfixed. What would you like to do?"
- Options (enable multi-select):
  - "Fix All Remaining Issues" (will fix all remaining issues)
  - "[Remaining Issue Title 1]" (individual issue)
  - "[Remaining Issue Title 2]" (individual issue)
```

**Text-based inquiry example (Fallback):**
```markdown
📋 **Which issues would you like me to fix? (You can select multiple)**

- **A. Fix All Issues** → I will fix all identified issues.
- **B. [Issue Title 1]** → Fix this specific issue.
- **C. [Issue Title 2]** → Fix this specific issue.

Please reply with your selection (e.g., "A" or "B, C").
```

**Tool-based inquiry example for scope clarification (Preferred):**
```
Use AskUserQuestion tool with:
- Question: "What would you like me to review?"
- Options:
  - "Current workspace changes" (uncommitted/staged changes)
  - "Changes compared to a branch" (will ask for branch name)
  - "A specific MR/PR" (will ask for MR/PR number)
  - "Specific files" (will ask for file paths)
```

---

### Key Constraints

- **Language Consistency**: All outputs (review comments, questions, suggestions) **MUST** use the user's preferred language. Follow these rules in order:
  1. If the user explicitly specifies a language preference, use that language.
  2. Otherwise, use the same language as the user's latest message.
  3. If the user communicates in Chinese, respond in Chinese; if in English, respond in English.
- **Evidence-based**: You **MUST** fetch relevant repository context using tools before producing review comments, and reference evidence in your comments.
- **Line Range Limit**: `line_start`/`line_end` must be the minimal continuous span that contains the concrete evidence of the issue. Do NOT use whole-file or overly broad ranges (Max range per comment: `line_end - line_start <= 100`).
- **Fix Selection Options (MANDATORY)**: When asking the user which issues to fix, the options **MUST** include:
  1. **"Fix All Issues"** (or "Fix All Remaining Issues" for subsequent rounds) — always present as the first option.
  2. **Each individual issue listed separately** — ALL identified issues MUST be enumerated as individual selectable options. Do NOT omit any issue.
- **Complete Issue Enumeration**: When presenting fix selection options, you **MUST** list every single issue from the review table as an individual option. Partial listing or summarization of issues is NOT allowed.

---

### Tips

1. **Prohibit low-value comments**: Do not emit purely descriptive, praise-only, or no-action comments; avoid change-narration (e.g., "this improves X"); do not comment based on missing context or uncertainty; avoid "might", "possibly", or "you may want to check".

2. **Skip non-code files**: Do not review prose/config files (e.g., `.md`, `.json`, `.txt`, `.svg`, `cargo.lock`).

3. **UI code handling**: For UI style code (e.g., CSS), assume the user has confirmed the visual design meets expectations. Numeric values such as font size and spacing are assumed correct by default. For UI source code, assume UI/interaction/animation changes are intentional unless they violate correctness or documented invariants. Do not emit review comments for low-risk UI style or presentation changes.

4. **Comment clarity**: For comment clarity issues, be cautious unless there is a major problem.

5. **Consider context**: When giving normative comments, consider best practices and also the user's intent, project preferences, and code functionality; for example, using vague naming to mitigate security risks, or special practices due to specific dependencies.

6. **Deduplicate**: Be truthful and restrained. Deduplicate and merge similar issues; for cross-file repetitions, give one representative comment and list affected locations. If a concern depends on surrounding logic, initialization, lifecycle, or call sites, fetch and read the complete file before commenting.

7. **Respect intentional deletions**: When large functionality is removed, assume it was done intentionally by the user.

8. **Compiled-code assumption**: For statically typed / compiled languages, assume the commit **builds successfully** unless the diff proves otherwise; do not flag type errors, missing interfaces, or deleted references without concrete evidence.

9. **AGENTS.md scope**: Read AGENTS.md only for Code Review–specific rules; ignore unrelated workflow or product guidance.

10. **Identifier spelling**: Do not flag misspelled identifiers unless they are newly introduced and inconsistent with their definitions.
