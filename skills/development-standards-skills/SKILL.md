---
name: development-standards-skills
description: Core system development standards, security-first architecture, defense in depth, conflict resolution priorities, and new feature readiness checklists. Triggers when the user asks for engineering standards, security architecture, or starts their message with /development-standards-skills or /standards.
---

# Core Development Standards & Engineering Philosophy

## 1. Overview & Core Philosophy
This skill defines the high-level engineering philosophy, enterprise security architecture, and quality standards for all development work across the repository. All contributions must reflect the discipline, foresight, and rigor of a Senior Systems Developer.

---

## 2. Security-First Architecture & Defense in Depth

### 2.1 Input Validation & Sanitization
- **Validate at System Boundaries:** All external input (HTTP parameters, GraphQL arguments, CLI arguments, and API payloads) must be strictly validated for type, range, format, and boundary lengths.
- **Sanitize Data:** Ensure untrusted input is properly sanitized before internal processing or persistence.

### 2.2 Injection Prevention
- **SQL & Query Injection:** Use parameterized queries, prepared statements, or ORM parameter binding (Eloquent/PDO). Never concatenate raw user input into SQL queries.
- **Command Injection:** Avoid invoking raw system shells with unescaped arguments. Use array argument passing or strict input validation.
- **XSS & Output Encoding:** Escape all user-supplied data before rendering in HTML/XML templates or UI components.

### 2.3 Authentication & Authorization
- **Strict Access Controls:** Enforce object-level and function-level access control (RBAC/ABAC) on every endpoint and GraphQL resolver using `@guard` and `@hasPermission`.
- **Principle of Least Privilege:** Grant only necessary system permissions for services, database users, and process execution.

### 2.4 Secret & Sensitive Data Management
- **Zero Secrets in Code:** Never commit passwords, API keys, private certificates, or access tokens into source files or documentation.
- **Environment & Vault Storage:** Store configuration secrets strictly in secure environment variables (`.env`) or dedicated secret managers.
- **Sensitive Data Exposure:** Mask or omit PII, tokens, and credentials in application logs and trace outputs.

---

## 3. Conflict Resolution & Priority Hierarchy
If two development standards or constraints appear to conflict, resolve them using this strict priority order:
1. **Security & Data Integrity** (Auth guards, transaction safety, SQL injection prevention, data sanitization)
2. **Correctness & Error Handling** (Bug-free execution, graceful null handling, structured error responses)
3. **Performance** (Prevent N+1 queries, eliminate heavy calculations in template loops, limit payload sizes)
4. **Architectural Consistency** (Shared templates, service layers, consistent patterns)
5. **Code Style & Formatting** (Variable naming, code placement, comment clarity)

---

## 4. Execution States & Intent Handling
- **Insufficient Context:** If critical files are missing or specifications are ambiguous, ask concise clarifying questions instead of making assumptions.
- **Code Review:** Output a Review Summary, state assumptions, cross-reference against constraints, output a violations table, and provide only modified sections.
- **Refactoring:** When modifying existing code, preserve public APIs, function signatures, database schemas, and GraphQL schemas unless explicitly requested to change them.
- **Code Generation:** Match the existing project's naming conventions, folder structure, dependency injection style, and import ordering.
- **Conceptual Questions:** Explain standards conceptually without hallucinating non-existent codebase entities.

---

## 5. Quick Checklist for New Features
Before marking any feature as complete:
1. **Security & Permissions:** Enforce `@guard` + `@hasPermission` on backend GraphQL fields; wrap UI controls with `<has-permission>`.
2. **Shared UI Components & Forms:** Use `app-button`, shared templates (`side-bar-template`, `drawer-template`, `layout-type-3`, `confirmation-modal`), Angular Material form controls (`mat-form-field`, `matInput`, `mat-select`, `mat-checkbox`) over legacy HTML form elements, and provide explicit fallback placeholder icons.
3. **UI Typography Defenses:** Apply `overflow-wrap: break-word`, `word-break: break-word`, and `min-w-0` on dynamic text containers to prevent layout blowouts.
4. **API Transactions & Exceptions:** Wrap database transactions safely without external I/O inside closures; catch `QueryException` and return `DatabaseExceptionHandler::handle(...)`.
5. **Eloquent Models:** Implement `Auditable` and `AuditableTrait` on models requiring audit trails; declare named constants for status values.
6. **Upload Limits:** Synchronize frontend byte limits with backend kilobyte limits (5MB or 10MB default).
7. **Database:** Execute migrations and seeds before writing dependent feature code.
8. **Automated Unit & Feature Tests:** Implement tests covering **happy**, **sad**, and **bad/invalid** paths with descriptive, non-conversational comments.
