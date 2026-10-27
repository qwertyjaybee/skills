---
name: pr-skills
description: Pull request, code review, diff discipline, and code modification guidelines ensuring minimal edits, no hallucinations, clean comments, precise variable naming, and structured review outputs. Triggers when the user asks for a PR or code review or starts their message with /pr-skills, /pr, or /review.
---

# Pull Request (PR) & Code Review Guidelines

## 1. Minimal & Targeted Code Modifications (Zero Unnecessary Edits)
- **Zero Hallucinations:** Never invent non-existent methods, properties, helper functions, packages, or models. Always verify existence in the active codebase before calling or referencing them. If something cannot be confirmed, inspect the file first or declare uncertainty rather than making assumptions.
- **Strict Scope Boundary:** Edit **only** the lines and files directly required to complete the task or resolve the bug. Never touch or edit code that does not need to be edited.
- **Helper Usage & Centralization:** Check for existing helper utilities before implementing custom logic. If logic/utility code will be executed multiple times or shared across components, extract it into a centralized helper method/class instead of duplicating it.
- **No Unrelated Refactoring:** Do not reformat intact code, modify unrelated variables, or rewrite existing logic unless explicitly instructed.
- **Preserve Formatting & Style:** Maintain existing project indentations, trailing commas, naming conventions, and docstrings.
- **Avoid Comment Deletion:** Never delete existing domain comments or documentation unless they are invalidated by the change.
- **Surgical Precision on Edits:**
  - Prefer concise, surgical, line-specific replacements over whole-file rewrites or broad block replacements.
  - Ensure every proposed edit has a concrete justification tied to functionality, security, or bug resolution.
  - Target only the exact lines requiring change; leave adjacent unmodified statements untouched.

---

## 2. Placement of New Code & Imports
- **New Code Always at the Bottom:** Always append newly added methods, functions, properties, constants, or types to the **last part / bottom** of the class, interface, type definition, or file, rather than prepending or inserting them at the top.
- **New Imports at the Bottom of Import Blocks:** Always place newly added `use` statements (PHP) or `import` statements (TypeScript/Angular) at the **bottom / last part** of the existing imports list, never at the top.
- **Use Imports Over Inline Qualified Names:** Always add proper `use` statements (PHP) or `import` statements (TypeScript/Angular) instead of using inline fully-qualified namespaces.

---

## 3. Informative & Clean Code Comments
- **Informative & Purpose-Driven:** Write informative, meaningful comments that explain the "why" and domain intent behind complex business logic or security decisions, rather than merely stating obvious syntax.
- **Concise & Direct:** Keep code comments objective, clear, and action-oriented. Avoid full narrative sentences or conversational filler.
- **No First-Person / Conversational Pronouns:** Do not use words like "we", "I", "our", or "us".
- **Examples:**
  - `// Cache public homepage sections dynamically using configured presigned TTL` (Informative & clear)
  - `// Update user status` (Concise)
  - Bad: `// Here we are updating the user status.` (Conversational)

---

## 4. Clear & Self-Explanatory Variable Naming
- **Easy to Understand at a Glance:** Always name variables clearly so their purpose and content are immediately understandable.
- **Avoid Cryptic Abbreviations:** Do not use vague or overly truncated abbreviations (e.g., `$sub`, `$aut`, `$q`, `$res`, `$subIds`, `$autIds`). Use clear names that reflect their domain entity (e.g., `$submission`, `$author`, `$query`, `$response`, `$submissionIds`, `$submissionAuthorIds`).
- **Meaningful Keys & Loop Variables:** Loop iterations and dictionary keys should be descriptive (e.g., `foreach ($submissions as $submission)` instead of `foreach ($subs as $s)`, `$targetKey` instead of `$key`).
- **Descriptive Collections:** Use descriptive pluralized names for arrays and collections (e.g., `$unprefixedParticipantIds`, `$submissionAuthors`).

---

## 5. Verification & Testing Protocol
- **Static Analysis & Linting:** Verify all modified code against project linter and static analysis rules prior to committing.
- **Targeted Unit Testing:** Run relevant test suites (PHPUnit, Karma/Jest) to verify functionality and ensure no regressions were introduced.
- **Empirical Validation:** Confirm bug fixes using concrete execution evidence, logs, or automated test output.

---

## 6. Code Review & PR Output Format
When conducting a PR code review, audit, or production readiness review, always format the response using the following structured report format:

### Report Template & Structure:

```markdown
# Production Readiness Review & PR Code Review Report
**Scope:** <repository / modules reviewed> (Branch `<branch-name>`)  
**Evaluation Standards:** `/pr-skills`, `/api-skills`, `/ui-skills`, `/development-standards-skills`  
**Status:** <ALL REMEDIATIONS COMPLETED — READY FOR PRODUCTION | REMEDIATION REQUIRED | PASS (Production Ready)>  
**Date:** <Formatted Date>

---

## 1. Executive Summary & Final Verdict

| Repository / Layer | Initial Verdict | Final Verdict | Critical Issues | Major Issues | Minor Issues | Total Files Evaluated |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `core-aairi/api` | PASS WITH ISSUES | PASS (Production Ready) | 0 | 0 | 0 | 10 |
| `core-aairi/ui`  | PASS WITH ISSUES | PASS (Production Ready) | 0 | 0 | 0 | 6 |

### Verdict Criteria:
- **PASS (Production Ready):** 0 Critical, 0 Major, 0 Minor issues remaining; fully compliant with security, transactional, and architectural standards.
- **PASS WITH ISSUES:** Minor/Major violations identified (naming, style, missing non-critical validation, OnPush, documentation).
- **FAIL:** ≥1 Critical violation (security vulnerability, authentication/authorization bypass, risk of data corruption, unhandled transaction rollback).

---

## 2. Final File Status (Good vs Bad)

Categorize every evaluated file under its respective repository or layer. Always link files with clickable markdown links (`[filepath](file:///absolute/path)`).

### 2.1 Backend (`core-aairi/api`)
| File Path | Status | Details |
| :--- | :--- | :--- |
| [`app/GraphQL/Mutations/.../Example.php`](file:///opt/core-aairi/api/app/GraphQL/Mutations/.../Example.php) | `GOOD` | Uses explicit `DB::beginTransaction()`, `DB::commit()`, `DB::rollBack()` in catches with `Log::info()`, lockForUpdate() on ordering. |
| [`app/GraphQL/Queries/.../Example.php`](file:///opt/core-aairi/api/app/GraphQL/Queries/.../Example.php) | `GOOD (Updated)` | Added strict column whitelisting on `$sortBy`, sanitized sort direction, removed dead code. |
| [`database/migrations/..._example.php`](file:///opt/core-aairi/api/database/migrations/..._example.php) | `GOOD` | Reversible down() method, indexed column. |

### 2.2 Frontend (`core-aairi/ui`)
| File Path | Status | Details |
| :--- | :--- | :--- |
| [`src/app/modules/.../example.component.ts`](file:///opt/core-aairi/ui/src/app/modules/.../example.component.ts) | `GOOD` | `ChangeDetectionStrategy.OnPush`, safe navigation operators `?.`, proper cleanup. |
| [`src/app/modules/.../example.component.html`](file:///opt/core-aairi/ui/src/app/modules/.../example.component.html) | `GOOD` | Proper tooltips, native form submission buttons, overflow-wrap on dynamic text. |

*Allowed Status values: `GOOD`, `GOOD (Updated)`, `BAD (Needs Fix)`, `FLAGGED`.*

---

## 3. Detailed Summary of Executed Fixes (or Violations & Remediations)

Group each issue or feature area into a dedicated subsection:

### 3.1 <Feature / Issue / Fix Title>
- **Problem:** Clear, technical description of the violation, bug, edge-case, or architectural defect.
- **Fix Applied:** Concrete, bulleted list of changes made to resolve the problem cleanly (schema updates, migrations, query ordering, UI bindings, etc.).

### 3.2 <Feature / Issue / Fix Title>
- **Problem:** ...
- **Fix Applied:** ...

---

## 4. Verification & Clean Status
- **Linter & Syntax:** Verified clean compilation and static analysis.
- **Git Hygiene:** Diffs are minimal, scoped strictly to required changes, zero extraneous edits or deletions of working code.
```

