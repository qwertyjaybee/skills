# Development Skills

A curated collection of engineering guidance for the project’s UI, API, and cross-stack work. Each skill is a self-contained `SKILL.md` that defines when it applies, the standards to follow, and the validation expected before work is considered complete.

## Available skills

| Skill | Purpose |
| --- | --- |
| [`ui-skills`](skills/ui-skills/SKILL.md) | Angular architecture, shared components, forms, accessibility, typography, and RxJS practices. |
| [`api-skills`](skills/api-skills/SKILL.md) | Laravel and Lighthouse GraphQL architecture, authorization, validation, transactions, queries, and error handling. |
| [`shared-skills`](skills/shared-skills/SKILL.md) | Standards shared between the UI and API, including permissions, module availability, uploads, and shared components. |
| [`development-standards-skills`](skills/development-standards-skills/SKILL.md) | Security-first engineering principles, conflict resolution, and feature readiness checklists. |
| [`planning-skills`](skills/planning-skills/SKILL.md) | Interactive implementation planning workflow for requests that explicitly require a plan. |
| [`findings-skills`](skills/findings-skills/SKILL.md) | Surgical resolution of code-review findings and bugs, including regression analysis and verification. |
| [`pr-skills`](skills/pr-skills/SKILL.md) | Pull request, code review, surgical diff discipline, and code modification guidelines. |
| [`commit-skills`](skills/commit-skills/SKILL.md) | Staged-only Git commit message generation (including staged new files) using the branch header and reader-friendly bullet format. |
| [`jira-description`](skills/jira-description/SKILL.md) | User-centric Jira Kanban task descriptions ("What Users See" & "What Users Can Do") supporting SED and FRD modes with MCP upload. |
| [`obsidian-skills`](skills/obsidian-skills/SKILL.md) | Comprehensive standards for Obsidian knowledge vault documentation, note templates, and consistent agent Markdown output formatting. |

## Using a skill

Read the relevant `SKILL.md` before implementing work governed by that skill. Skills may be invoked by their name or by their documented command prefix, such as `/ui`, `/api`, `/shared`, `/plan`, `/findings`, `/pr`, `/commit`, `/jira-description`, or `/obsidian`.

When more than one skill applies, use the smallest set that covers the task. Cross-stack changes generally require both the relevant UI or API skill and [`shared-skills`](skills/shared-skills/SKILL.md).

## Engineering principles

- Validate and sanitize all input at system boundaries.
- Enforce authentication, authorization, and module availability consistently.
- Protect secrets and sensitive data; never commit credentials.
- Preserve existing public contracts unless a change is explicitly requested.
- Prefer shared components and established project patterns over one-off implementations.
- Verify changes with focused tests, linting, or an appropriate manual check.

## Repository layout

```text
.
├── README.md
├── skills.json
├── automation/
│   └── jira-description/
│       ├── README.md
│       └── SKILL.md
└── skills/
    ├── api-skills/
    ├── commit-skills/
    ├── development-standards-skills/
    ├── findings-skills/
    ├── planning-skills/
    ├── pr-skills/
    ├── shared-skills/
    ├── ui-skills/
    └── obsidian-skills/
```

Each skill directory can evolve independently, but its `SKILL.md` should remain clear about scope, trigger conditions, implementation rules, and verification requirements.
