---
name: obsidian-skills
description: Comprehensive standards and conventions for Obsidian knowledge vault documentation, note creation, and consistent agent Markdown output formatting. Triggers when writing project documentation, architectural decision records (ADRs), technical summaries, task logs, or when the user invokes /obsidian or /obsidian-skills.
---

# Obsidian Output & Documentation Guidelines

## 1. Overview & Core Philosophy
This skill governs how technical documentation, architectural notes, feature specifications, API/UI guides, and execution summaries are formatted so they are 100% compatible with Obsidian and consistently structured.

The project vault resides in `/opt/core-aairi/docs/` and can be opened directly as an independent Obsidian vault.

---

## 2. Note Structure & Frontmatter (YAML)

Every markdown document created in `docs/` or intended as an Obsidian note **MUST** begin with a valid YAML frontmatter block:

```yaml
---
title: "Descriptive Note Title"
date: YYYY-MM-DD
last_modified: YYYY-MM-DD
tags:
  - tag1
  - tag2
type: adr | feature | api-doc | ui-doc | task-summary | guide | index
status: draft | proposed | accepted | active | completed | deprecated
---
```

### Frontmatter Fields:
- `title`: Explicit, human-readable title enclosed in double quotes.
- `date`: Creation date in `YYYY-MM-DD` format.
- `last_modified`: Last modification date in `YYYY-MM-DD` format.
- `tags`: Lowercase, hyphen-separated tags (e.g., `api`, `graphql`, `ui`, `angular`, `adr`, `task-summary`).
- `type`: Category indicator corresponding to the note's purpose.
- `status`: Lifecycle status.

---

## 3. Obsidian Callout Conventions

Always use native Obsidian / GitHub Flavored Markdown callout blocks instead of plain indented blockquotes. Callouts draw visual attention to critical considerations, summaries, and warnings.

### Standard Callout Types:
```markdown
> [!NOTE] Context & Highlights
> Background information, design rationale, or relevant context.

> [!TIP] Best Practices & Performance
> Helpful implementation hints, shortcuts, or performance optimizations.

> [!IMPORTANT] Critical Requirements
> Essential preconditions, strict rules, or invariants that must not be broken.

> [!WARNING] Potential Risks & Breaking Changes
> Deprecation notices, transaction boundaries, or breaking changes.

> [!CAUTION] Security & Data Integrity
> High-risk operations, authorization rules, and data loss precautions.

> [!SUMMARY] Executive Summary
> Quick synopsis or TL;DR placed near the top of the note.
```

---

## 4. Bi-directional Links & Wikilinks

1. **Internal Vault Links:** Use Obsidian wikilinks `[[Target Note Name]]` or `[[Path/Target Note Name|Display Text]]` when referencing other notes within the `docs/` vault.
   - Example: `[[00 - Index|Vault Index]]`
   - Example: `[[Architecture/adr/ADR-001 - Obsidian Knowledge Vault Integration|ADR-001]]`
2. **Codebase File Links:** When referencing source code outside `docs/` in agent responses, use markdown links with relative paths or standard file URI scheme:
   - Example: `[schema.graphql](file:///opt/core-aairi/api/graphql/schema.graphql)`
3. **MOC Integration:** Whenever creating a new note in `Architecture/`, `API/`, `UI/`, or `Tasks/`, ensure it is linked back to the relevant section's `README.md` or `docs/00 - Index.md`.

---

## 5. Visualizations & Diagrams (Mermaid)

Use Mermaid diagrams to visualize architectures, component relationships, state machines, and workflows:
- Supported diagram types: `flowchart TD` / `flowchart LR`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`, `classDiagram`.
- Always quote labels containing special characters, brackets, or parentheses (e.g., `node["Label (Details)"]`).
- Keep diagrams focused, legible, and uncluttered.

---

## 6. Directory Placement & Naming Conventions

Place all generated documentation within the appropriate `docs/` subfolder:
- `docs/Architecture/adr/`: Architecture Decision Records (`ADR-XXX - Title.md`)
- `docs/API/`: Backend GraphQL modules and services (`<Domain> - <Feature>.md`)
- `docs/UI/`: Frontend Angular components and modules (`<Module> - <Component>.md`)
- `docs/Infrastructure/`: DevOps, Docker, AWS, and deployment notes
- `docs/Tasks/`: Completed task execution summaries (`YYYY-MM-DD - Task Name.md`)
- `docs/Templates/`: Reusable Obsidian note templates

---

## 7. Templates Catalog

Refer to standard templates in `docs/Templates/`:
- `Template - Architecture Decision Record.md`
- `Template - Feature Specification.md`
- `Template - GraphQL API Module.md`
- `Template - Angular UI Component.md`
- `Template - Task Execution Summary.md`

