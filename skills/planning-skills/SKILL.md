---
name: planning-skills
description: Step-by-step implementation planning workflow outputting an interactive Markdown artifact with review, comments, and a Proceed button, strictly waiting for user approval before making any code modifications. Triggers ONLY when the user explicitly asks for an implementation plan or starts their message with /planning, /planning.md, or /plan. If the user does not explicitly request an implementation plan, do NOT create one.
---

# Implementation Planning Guidelines

## 1. Overview & Core Philosophy
This skill governs how implementation plans are constructed, presented, and approved before code changes occur.

**MANDATORY TRIGGER RULE:**
- **Explicit Request Required:** ONLY create an implementation plan when the user explicitly requests one (e.g., using `/plan`, `/planning`, `/planning.md`, or asking "create an implementation plan", "plan this first", etc.).
- **No Plan by Default:** If the user did NOT explicitly ask to create an implementation plan, DO NOT create an implementation plan artifact or block on plan approval. Proceed directly with the requested task or minimal, direct code modifications.
- When an implementation plan is explicitly requested, all plans must be created as interactive artifacts with `RequestFeedback: true` so the user can review, comment, and click "Proceed" before code changes take place, without generating temporary plan files inside the repository codebase.

---

## 2. Planning Workflow & Output Format

### 2.1 Interactive Artifact Plan (With Review & Proceed Action)
- When formulating an implementation plan, create the plan as a Markdown artifact file in the conversation artifacts directory (`<appDataDir>/brain/<conversation-id>/<plan_name>.md`) using `write_to_file`.
- **Interactive Review & Proceed Gate:** Always set `ArtifactMetadata.RequestFeedback: true` and `ArtifactMetadata.UserFacing: true` so the UI presents the user with an interactive review panel, comment capability, and a clickable **Proceed** button.
- **Zero Repository Files:** DO NOT create, write, or persist implementation plan files (e.g. `planning.md`, `plan.md`, `implementation_plan.md`) into the repository workspace. Only save them in the Antigravity conversation artifact directory.

### 2.2 Plan Structure
Every plan should follow a disciplined structure:
1. **Problem Analysis & User Requirements:**
   - Clearly restate the core requirements, root cause, or feature expectations.
   - Note critical architectural boundaries (e.g., shared components that must not be broken or edited, security constraints, performance impact).
2. **Proposed Changes:**
   - Group by feature area or architectural layer (e.g., Models, Services, Components, SCSS/Styling, Types/Constants).
   - Detail specific modifications, helper functions, and logic handling.
   - If UI forms or inputs are involved, strictly adhere to Angular Material and Reactive Forms standards (no legacy HTML form elements).
3. **Scope & Files to Modify:**
   - Explicit list of files that will be modified or created.
   - Explicit list of files that are intentionally left untouched.
4. **Verification & Testing Protocol:**
   - Concrete test cases, validation checks, edge-case scenarios, and build verification steps (`ng build`, PHPUnit tests, etc.).

---

## 3. Strict Stop Before Execution (Approval Gate)
- **Halt Immediately After Creating Artifact Plan:** Once the plan artifact is written with `RequestFeedback: true`, the agent MUST stop execution immediately to allow the user to review, comment, and click "Proceed".
- **Zero Premature Code Edits:** DO NOT call any repository code-editing tools or execute state-modifying shell commands in the same turn.
- **Wait for Explicit Approval / Proceed:** Await the user clicking the "Proceed" button or providing approval / feedback before executing any modifications.

---

## 4. Skill & Standard Cross-Referencing
Before presenting the plan, always consult relevant skills:
- **UI Changes:** Reference `ui-skills` (Angular Material form controls, `app-button`, typography defenses, TipTap WYSIWYG sanitization).
- **Backend / API Changes:** Reference `api-skills` (GraphQL schemas, transactions, `@guard`, `@hasPermission`, exceptions).
- **PR & Code Discipline:** Reference `pr-skills` (surgical diffs, zero hallucinations, clean informative comments).
- **General Standards:** Reference `development-standards-skills` (defense in depth, conflict resolution hierarchy).
