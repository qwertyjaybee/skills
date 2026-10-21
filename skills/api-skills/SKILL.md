---
name: api-skills
description: Comprehensive backend standards and guidelines for Laravel and Lighthouse GraphQL development in the project, including schemas, resolvers, directives, transactions, error handling, models, and automated tests. Triggers when the user asks for backend/API guidelines or starts their message with /api-skills or /api.
---

# Laravel & Lighthouse GraphQL API Development Standards

## 1. Architecture & Code Structure
- **Schema Organization:** Located under `api/graphql/` grouped by domain. Split into `.query.graphql`, `.mutation.graphql`, `.types.graphql`, `.input.graphql` as appropriate, aggregated via `schema.graphql`.
- **Resolvers:** `api/app/GraphQL/Queries/…` and `api/app/GraphQL/Mutations/…` organized per module/feature (mirroring GraphQL folder where practical).
- **Types (PHP):** `api/app/GraphQL/Types/` (e.g. `Error`, `Success`, payload types).
- **Placement of New Code & Imports:**
  - Always append newly added methods, functions, properties, constants, or routes to the **last part / bottom** of the class, interface, or file.
  - Always place newly added `use` statements at the **bottom / last part** of the imports block, never at the top.
  - Always add proper `use` statements instead of using inline fully-qualified namespaces (e.g., use `\Illuminate\Support\Facades\Cache` at the bottom of imports, not inline).

---

## 2. Security, Directives & Authorization
- **Strict Access Control:** Enforce object-level and function-level access control on every endpoint and GraphQL resolver using `@guard` and `@hasPermission`.
  ```graphql
  myField: MyType
    @guard(with: ["api"])
    @hasPermission(permission: "view-module-management")
  ```
  - The directive `App\GraphQL\Directives\HasPermissionDirective` checks `Auth::user()->can($permission)` and throws Lighthouse's `AuthenticationException` if missing or denied.
- **Throttling Directive (`@throttle`):**
  - Directive class: `App\GraphQL\Directives\ThrottleDirective` (`api/app/GraphQL/Directives/ThrottleDirective.php`).
  - Schema usage:
    ```graphql
    someField: SomeType @throttle(limit: 10, decay: 60)
    ```
  - Parameters:
    - `limit`: Max requests within the window (default `10`).
    - `decay`: Window length in seconds (default `300`).
    - `Key`: Derived from request IP, authenticated user id, and `username` argument when present (`resolveThrottleKey`).
  - Apply `@throttle` on sensitive or high-traffic fields (auth flows, heavy listing queries).
  - Prefer throttling non-admin or broadly authenticated non-privileged callers so operational users are not blocked.
- **Visibility First:** Check visibility and ownership permissions *before* querying child relations.
- **Redaction:** Obscure private attributes via API Resources, DTOs, or GraphQL transformers. DO NOT mutate live database models in memory.

---

## 3. Database Transactions & Cache Safety
- **Transaction Closures:** Prefer `DB::transaction(function() { ... })` over manual `beginTransaction()` and `commit()`.
- **Manual Rollback Safety:** When manual `DB::beginTransaction()` is strictly required, ensure all early return/exit paths within the transaction block call `DB::rollBack()` explicitly.
- **CRITICAL: Transaction Safety:** DO NOT execute external I/O (file uploads, S3 operations, HTTP calls, email sending) inside a database transaction. Dispatch these to a queue or execute them after the transaction successfully commits.
- **Transient Cache Safety:** Wrap `Cache::remember()` in a try/catch block rather than putting the try/catch inside the closure. Always calculate cache TTL dynamically using the config value (e.g., converting `filesystems.presigned_url_expiration` to seconds) instead of hardcoding TTLs.

---

## 4. Error Handling & Validation
- **Exception Handling with `DatabaseExceptionHandler`:**
  - Class: `App\Helpers\DatabaseExceptionHandler\DatabaseExceptionHandler` (`api/app/Helpers/DatabaseExceptionHandler/DatabaseExceptionHandler.php`).
  - When catching `Illuminate\Database\QueryException`, return a structured GraphQL `Error` type instead of leaking raw SQL or internal database exception messages:
    ```php
    DatabaseExceptionHandler::handle(
        QueryException $e,
        array $customMessages = [],
        string $defaultMessage = 'A database error occurred'
    ): Error
    ```
  - `$customMessages` keys can target constraint names, column names, or reserved keys such as `default`, `unique`, `email`, `username`, `alias`, `composite_parent_name`, etc.
  - For authorization and validation, rely on standard exception bubbling.
- **Graceful Null Dereferencing:** Verify model existence before dereferencing attributes in GraphQL resolvers. Return a structured GraphQL `Error` if the record does not exist.
- **Input Validation:** All external input must be strictly validated for type, range, format, and boundary ceilings (e.g. string length ceilings like 250 characters).
- **Parameterized Queries:** Use parameterized queries, prepared statements, or Eloquent/PDO bindings. Never concatenate raw user input into SQL queries.

---

## 5. Eloquent Models & Queries
- **Auditing:** Ensure models requiring an audit trail implement `Auditable` and use `AuditableTrait`:
  ```php
  use OwenIt\Auditing\Contracts\Auditable;
  use OwenIt\Auditing\Auditable as AuditableTrait;

  class ExampleModel extends Model implements Auditable
  {
      use AuditableTrait;
  }
  ```
- **Named Status Constants:** Define named constants on models for discrete or status values (avoid magic numbers or strings):
  ```php
  public const ACTIVE = 1;
  public const INACTIVE = 0;
  public const STATUS_PUBLIC = 3;
  ```
- **Eager Loading:** Eager load relations (e.g., `with(['media'])`) to eliminate N+1 queries, unless DataLoader is utilized or media is not requested.
- **Pagination:** List queries must be paginated following the project's strategy unless the list is demonstrably bounded (e.g., enums, fixed status lists).
- **Database Migrations & Seeds:** Always execute seeds and migrations before starting feature development.

---

## 6. Navigation Config Pattern
- Navigation is configured in `api/config/navigation.php` and split into per-parent configs under `api/config/navigation/`.
- Create one file per parent group under `api/config/navigation/`.
- Match parent key in `api/config/navigation.php` (e.g. `pages.php`, `posts.php`, `appearance.php`).
- Register new parent groups in `api/config/navigation.php`.

---

## 7. Automated Testing & Path Coverage
For every new feature, model, mutation, or query, generate a dedicated automated test suite covering:
- **Happy Path (Normal Execution):**
  - Verify standard successful workflows, valid inputs, expected outputs, and successful state transitions or database persists.
  - Verify default attribute assignments, slug generation, timestamp updates, and correct user auditing.
- **Sad Path (Expected Domain Rejections):**
  - Verify domain-level rejections (inactive parent entities, duplicate records/titles, collisions, resource not found, no-op updates).
  - Verify informative domain error messages and structured error types (`App\GraphQL\Types\Error` or HTTP responses) without executing unneeded database writes or state changes.
- **Bad Path (Invalid Input, Malformed Data & Boundary Violations):**
  - Verify strict validation failures on missing required fields, empty or whitespace-only strings, out-of-range numerical values, invalid enum/status values, and boundary overflows (>250 characters).
  - Verify defensive exception handling: SQL/database constraint errors, unique violations, or data truncation errors trapped gracefully via `DatabaseExceptionHandler`.
  - Verify authorization guards (`@guard`, `@hasPermission`): unauthenticated or unauthorized requests must be rejected.
- **Test Comments:** Accompany each test method with clear, informative docstrings explaining the tested scenario.
