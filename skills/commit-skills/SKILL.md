---
name: commit-skills
description: Generates clear, reader-friendly Git commit messages strictly from staged files (including staged new files) using the project's branch-header and bullet-point format. Triggers when the user asks to create or generate a commit message, or starts their message with /commit, /commit-skills, or /commit-message.
---

# Commit Message Generation Guidelines

## 1. Absolute Staged-Files-Only Rule
Commit messages must be generated **strictly and exclusively from files currently staged in Git** (`git diff --staged` / `git diff --cached`).

- **Inspect Staged Changes Only:**
  - Retrieve the active branch name using `git branch --show-current`.
  - Inspect only staged files and their diffs using `git diff --staged --name-status` and `git diff --staged`.
  - This includes staged modifications (`M`), staged deletions (`D`), and newly created files that have been staged (`A`).
- **Strictly Ignore Unstaged & Untracked Files:**
  - **Never** read or include untracked files (`??`) that have not been staged with `git add`.
  - **Never** read or include unstaged working-tree modifications to tracked files (` M` or `git diff`).
- **No Staged Files Rule (Mandatory Stop):**
  - If `git diff --staged` is empty (no files are staged in the target repository), **DO NOT generate a commit message**.
  - Immediately inform the user:
    > "No files are currently staged. Please stage the changes you want to commit (e.g., `git add <files>`) and run `/commit-skills` again."
- **No Unsolicited Commits:**
  - Output the formatted commit message for the user to review and copy. Do not execute `git commit` unless explicitly instructed by the user.

---

## 2. Required Commit Message Format
Every commit message must strictly follow this structure:

```text
{{branch name}}
  •   {{message 1}}
  •   {{message 2}}
```

### Formatting Rules:
1. **Line 1 (Header):** Exact current branch name (`{{branch name}}`, e.g., `AIRI-284` or the full branch title). Do not prefix or alter the branch name unless the user specifies a title suffix.
2. **Bullet Lines:**
   - Prefix each bullet with **two spaces, a bullet character `•`, and three spaces** (`  •   `).
   - Start each bullet message with a lowercase action verb (e.g., `add`, `update`, `remove`, `fix`, `order`, `enforce`, `prevent`) for consistency with project commit history.
   - Use **one bullet** when all staged files belong to a single cohesive feature or fix.
   - Use **two or more bullets** when multiple distinct features, enhancements, or fixes are added or modified across the staged files.

---

## 3. Clarity & Readability Standards
Commit messages are written for human readers (developers, reviewers, QA, and stakeholders), not compilers.

### Do:
- **Explain the Feature or Behavior Change:** Describe *what* capability was added, modified, or fixed in clear, plain domain language.
- **Group Related File Edits:** Synthesize related staged changes (e.g., component HTML, TypeScript, SCSS, and service updates for one feature) into clear feature-level bullet points rather than listing file-by-file edits.

### Do Not:
- **No Generic / Vague Messages:** Never write meaningless summaries such as:
  - `update files`
  - `fix bug`
  - `refactor code`
  - `minor UI changes`
- **No Raw Function, Class, or Query/Mutation Names:** Never write commit messages that merely echo internal code identifiers, method names, component class names, or GraphQL query/mutation names.

### Examples (Good vs. Bad):

| Staged Change Context | Bad (Generic or Code/Query Name) | Good (Clear & Reader-Friendly) |
| :--- | :--- | :--- |
| Added `sort_order` column migration and updated `GetMembershipTiers` query ordering | `update GetMembershipTiers query and migration` | `order membership tiers by sort order on the public page` |
| Updated `MembershipTierComponent` (`handleDrop`, `removePagination`) and template | `modify handleDrop and ngOnInit in MembershipTierComponent` | `add drag-and-drop hierarchy reordering for membership tiers`<br>`remove pagination in membership tier management view` |
| Added `@hasPermission` guard and input validation to event registration resolver | `update RegisterEventMutation.php` | `enforce permission checks and input validation on event registration` |

### Complete Output Example:
```text
AIRI-284
  •   add drag-and-drop hierarchy reordering for membership tiers
  •   remove pagination and optimize tier reordering logic in membership tier management
```

