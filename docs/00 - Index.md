---
title: "Project Knowledge Base Index"
date: 2026-11-05
last_modified: 2026-11-05
tags:
  - moc
  - index
  - architecture
  - project-knowledge
type: index
status: active
---

# Project Knowledge Base

Welcome to the **core-aairi** Obsidian knowledge vault. This vault centralizes system architecture documentation, GraphQL API modules, Angular UI components, task execution logs, and engineering templates.

> [!INFO] Obsidian Vault Root
> This directory (`docs/`) is configured as an independent Obsidian vault. You can open `/opt/core-aairi/docs` in Obsidian to view graph views, backlinks, canvas boards, and formatted notes.

---

## 🗺️ Map of Content (MOC)

| Section | Description | Key Notes / Directory |
| :--- | :--- | :--- |
| **[[Architecture/]]** | High-level system design, domain boundaries, and ADRs | `Architecture/` & `Architecture/adr/` |
| **[[API/]]** | Laravel 12 & Lighthouse GraphQL backend documentation | `API/` |
| **[[UI/]]** | Angular 19 admin frontend modules, shared templates & styles | `UI/` |
| **[[Infrastructure/]]** | Docker compose, AWS Cognito, S3, CloudFront & deployment | `Infrastructure/` |
| **[[Tasks/]]** | Implementation summaries, task logs, and audit trails | `Tasks/` |
| **[[Templates/]]** | Standard note templates for consistent documentation | `Templates/` |

---

## 📐 Quick Links & Architecture Decision Records (ADRs)

- Architecture Decision Records live in `Architecture/adr/` following the format: `ADR-XXX - Title.md`.
- See [[Templates/Template - Architecture Decision Record|ADR Template]] to create a new decision record.

---

## 🛠️ Note Templates Catalog

- [[Templates/Template - Architecture Decision Record|Template: Architecture Decision Record (ADR)]]
- [[Templates/Template - Feature Specification|Template: Feature Specification]]
- [[Templates/Template - GraphQL API Module|Template: GraphQL API Module]]
- [[Templates/Template - Angular UI Component|Template: Angular UI Component]]
- [[Templates/Template - Task Execution Summary|Template: Task Execution Summary]]

> [!TIP] Agent Output Consistency
> Whenever Antigravity creates or updates technical notes, it references the standards defined in `obsidian-skills` to maintain consistent frontmatter, callouts, and structure.

