---
name: findings-skills
description: Fixes reported code findings and bugs with senior-level precision. Evaluates regression risks, limits edits strictly to the findings, and triggers the planning-skills workflow to generate an interactive implementation plan before making code changes. Triggers on /findings, /finding, /findings-skills, or when addressing code review and audit findings.
---

# Findings & Bug Resolution Guidelines

## 1. Overview & Senior Mindset
This skill governs how to address code review findings, bug reports, and audit issues. When invoked, assume the role of a **Senior Developer / Lead Engineer** with deep expertise in root-cause debugging, surgical code remediation, and defensive software engineering.

**Core Principles:**
- **Root Cause over Symptom:** Identify and fix the true underlying bug rather than applying superficial patches.
- **Strict Scope Boundary:** Edit **only** what is necessary to resolve the specific findings. Zero unrelated refactoring or code cleanup.
- **Regression Hunting:** Actively hunt for and protect against any potential regressions or side effects that could break existing functionality or dependent modules.
- **Implementation Plan First:** Always invoke the `planning-skills` workflow before writing or modifying code.

---

## 2. Mandatory Planning Integration
When addressing findings:
1. **Consult Planning Skill:** Read and strictly follow [.agents/skills/planning-skills/SKILL.md](file:///opt/core-aairi/.agents/skills/planning-skills/SKILL.md).
2. **Interactive Plan Artifact:**
   - Create a dedicated implementation plan artifact inside `<appDataDir>/brain/<conversation-id>/<plan_name>.md` via `write_to_file`.
   - Set `ArtifactMetadata.RequestFeedback: true` and `ArtifactMetadata.UserFacing: true`.
   - **Never** write planning files (e.g. `planning.md`, `plan.md`) into the repository workspace.
3. **Approval Gate:**
   - Halt execution immediately after writing the plan artifact.
   - Do NOT edit any repository code until the user clicks **Proceed** or provides explicit approval.

---

## 3. Strict Scope & Surgical Edits
Adhere strictly to [.agents/skills/pr-skills/SKILL.md](file:///opt/core-aairi/.agents/skills/pr-skills/SKILL.md):
- **Targeted Modifications Only:** Touch only the exact lines and files directly involved in the finding.
- **No Scope Creep:** Never reformat untouched code, rename unrelated variables, or modify working logic outside the finding's scope.
- **No Hallucinations:** Verify that all referenced methods, properties, models, or types exist in the active codebase before using them.
- **Code Placement:** Append new helper methods, properties, or types to the bottom/last part of classes/files. Place new `use` (PHP) or `import` (TS) statements at the bottom of the existing import block.
- **Clean Variable Naming & Comments:** Use descriptive, self-explanatory variable names (avoid cryptic abbreviations like `$sub`, `$q`, `$res`). Domain comments must be informative, objective, and devoid of conversational pronouns ("we", "I").

---

## 4. Senior Regression Risk Analysis
Before formulating the fix, conduct a thorough regression risk assessment and document it in the implementation plan:

### 4.1 Downstream & Upstream Impact
- **Callers & Consumers:** Search for all references to the modified functions, components, or services across the codebase. Ensure signature changes do not break existing callers.
- **API Contracts:** Check if changes alter GraphQL schemas, query responses, or payload structures expected by the frontend.
- **Database & Data Integrity:** Verify that fixes do not corrupt existing data, bypass transactions, or violate database constraints.

### 4.2 State & Lifecycle Defenses (UI / Angular)
- **Lifecycle Side Effects:** Ensure fixes do not cause infinite change detection loops, premature subscriptions, or unhandled component destruction leaks (use `takeUntilDestroyed()`).
- **Reactive Forms & Inputs:** Confirm form control validation, touched/dirty states, and disabled states remain consistent with user expectations.
- **Styling & Layout:** Verify changes do not unintentionally alter parent containers, responsive layouts, or shared CSS classes.

### 4.3 Security & Authorization Defenses (API / Laravel)
- **Permissions & Guards:** Confirm that fixes maintain all `@guard`, `@hasPermission`, and role-based policies.
- **Input Validation & Sanitization:** Ensure user inputs remain validated and sanitized against injection and tampering.

---

## 5. Finding Resolution Plan Structure
The implementation plan artifact generated for findings must include:
1. **Finding Summary & Root Cause Analysis:**
   - Accurate description of the finding and the underlying root cause.
2. **Regression Risk Assessment:**
   - List of potentially affected modules, components, callers, or tests.
   - Explicit defensive measures taken to neutralize regression risks.
3. **Proposed Surgical Changes:**
   - Exact files to touch and description of the targeted fix.
   - Explicit confirmation of files/components left untouched.
4. **Verification & Testing Protocol:**
   - Precise unit tests, lint checks, or manual reproduction steps to confirm the bug is fixed and no regressions occurred.
