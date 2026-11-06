---
title: "ADR-001: Obsidian Knowledge Vault Integration"
date: 2026-11-05
last_modified: 2026-11-05
tags:
  - adr
  - architecture
  - documentation
  - obsidian
status: accepted
superseded_by: ""
type: adr
---

# ADR-001: Obsidian Knowledge Vault Integration

> [!NOTE] Status
> **Current Status:** `accepted` | Date: `2026-11-05`  
> **Deciders:** User, Antigravity Agent

---

## 1. Context & Problem Statement
The repository contains multiple subsystems across backend (`api`), frontend (`ui`), infrastructure (`infra`), and AI agent guidance (`.agents`). Historically, architectural decisions and technical notes were dispersed or lacked a unified output standard. The user requested implementing Obsidian in the project so that agent outputs, technical documentation, and knowledge artifacts remain consistent, connected, and easily browseable.

---

## 2. Considered Options
1. **Option 1 (Chosen): Dedicated Root Vault in `docs/` with Agent Output Skill (`obsidian-skills`).**
   - Self-contained Obsidian vault directly inside `/opt/core-aairi/docs`.
   - Pre-configured `.obsidian/` settings and core plugins.
   - Standard templates for ADRs, feature specs, API docs, UI components, and task logs.
   - Dedicated agent skill enforcing frontmatter, callouts, and wikilinks.
2. **Option 2: Storing notes inside `.agents/notes/`.**
   - Keeps documentation buried inside the hidden `.agents/` folder, making it less accessible for standard team onboarding or standard documentation viewers.
3. **Option 3: External Wiki or Third-Party Tool (Notion / Confluence).**
   - Disconnected from the git repository, vulnerable to sync drift, and cannot be updated directly within code reviews or agent workflows.

---

## 3. Decision Outcome
Chosen Option: **Option 1**, because it provides git-tracked, version-controlled documentation that can be opened immediately in the Obsidian desktop application as a local vault, while providing structured templates and agent skills for consistent output.

### Positive Consequences
- Agent technical summaries, feature specifications, and architectural logs adhere to a strict, predictable format.
- Bidirectional linking (`[[...]]`) and graph views in Obsidian illuminate relationships between backend models, frontend views, and infrastructure.
- Zero external dependencies; all notes are clean, standard GitHub Flavored Markdown with KaTeX math and Mermaid support.

### Negative Consequences / Trade-offs
- Developers and agents must maintain discipline when adding new notes by following frontmatter and naming conventions.

---

## 4. Implementation Notes & References
- Vault root: `docs/`
- Index / MOC: [[00 - Index|Vault Index]]
- Agent skill: `.agents/skills/obsidian-skills/SKILL.md`
- Templates: `docs/Templates/`

