---
name: api-skills
description: Comprehensive backend standards and guidelines for Laravel and Lighthouse GraphQL development in the project, including schemas, resolvers, directives, module availability, transactions, error handling, models, navigation, and automated tests. Triggers when the user asks for backend/API guidelines or starts their message with /api-skills or /api.
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
- **Module Availability Integration:** Every GraphQL field must have exactly one module check:
  - If a field has `@hasPermission`, the module check is derived automatically from the permission's mapping in `api/config/modules/*.php`. **Do not add `@moduleAvailable`**.
  - If a field uses `@guard` only (self-service/logged-in users) or is public (no login), it **must** include `@moduleAvailable(module: "<key>")`.
  - See [Section 8: Module Availability Standards](#8-module-availability-standards-module-management--feature-flags) for complete rules.
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
- **Module Availability Mapping:** Every entry in `api/config/navigation/*.php` must carry `'module' => '<key>'` referencing its corresponding node in `api/config/modules/<root>.php`.

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

---

## 8. Module Availability Standards (Module Management & Feature Flags)
Every new feature, screen, or permission must declare the module it belongs to, in both the API and the UI, in the same change. Module Management allows administrators to switch an entire feature off, and that switch strictly overrides role permissions.

### Why Module Mapping Is Mandatory
If a feature is not declared in the module tree:
1. **Admins cannot switch it off:** It keeps working even when its parent module is disabled.
2. **Permissions show as `Unassigned`:** On the admin Module Management screen.
3. **`ModuleSeederTest` fails:** Rejects any permission lacking a module mapping or description.

The module tree is defined in `api/config/modules/<root>.php`, one file per top-level area. Its keys (for example, `certificate.types`) are the shared vocabulary between the API, UI routes, and navigation.

---

### API & GraphQL Directive Enforcement
Each GraphQL field gets **exactly one module check**. Fields with a permission are covered by the permission check. Every other field needs `@moduleAvailable`.

| Field Directive / Scenario | Where Module Check Originates | Add `@moduleAvailable`? |
| :--- | :--- | :--- |
| **`@hasPermission(...)`** | The permission's module, from `config/modules/*.php` | **No** (Never add both) |
| **`@guard` only** (logged-in user, e.g. "my membership") | Nothing (guard only checks auth) | **Yes** |
| **Neither** (public, no login required) | Nothing | **Yes** |

#### Why `@hasPermission` Is Enough
- `App\GraphQL\Directives\HasPermissionDirective` first checks whether every permission that could grant access is in a switched-off module. If so, it immediately rejects with `"This module is currently unavailable."`, the same message `@moduleAvailable` uses. Only then does it check the user's role.
- `User::hasPermissionTo()` is overridden to return `false` for permissions in a switched-off module, so `$user->can(...)` inside resolvers follows the switch automatically.
- Each permission is mapped to exactly one module node, so the permission already names its module.
- **NEVER put both directives on one field:** While it may execute, it introduces a redundant hand-typed key that drifts out of date if the permission is later relocated to another module.
- **`@guard` only checks authentication:** It does NOT check modules. Self-service authenticated fields must declare `@moduleAvailable`:
  ```graphql
  applyMembership: Message!
    @field(resolver: "App\\GraphQL\\Mutations\\Membership\\Apply")
    @guard(with: ["api"])
    @moduleAvailable(module: "membership.my-membership")
  ```

---

### Step-by-Step API Implementation Checklist
1. **Permission Constant:** Add each new permission to `config/constants.php` under `BASE_PERMISSIONS` (or `GUEST_PERMISSIONS`).
2. **Map to One Module:** Add it, with a plain-language description, under **exactly one node** in `config/modules/<root>.php`. Choose the module that owns the feature, not the screen where it appears.
3. **New Feature Area = New Child Node:** Key child nodes as `<parent.key>.<slug>`. A new top-level area gets its own `config/modules/<key>.php`, named after its root key. Never rename or reuse a seeded key, because the UI and navigation refer to it. Set `'is_system' => true` only for modules that must never be switched off.
4. **Schema Directives:** Put `@hasPermission` or `@moduleAvailable(module: "<key>")` on every query and mutation (following the single-check table above).
5. **Navigation Entry:** Every entry in `config/navigation/*.php` gets `'module' => '<key>'`.
6. **Seed, Never Migrate:** Permissions, roles, role grants, navigation, and modules are written by seeders (`BasePermissionSeeder`, role seeders, `ModuleSeeder`, `NavigationSeeder`). Migrations are schema only. Seeders only fill in what's missing, and `ModuleSeeder` never overwrites an admin's changes.
7. **Automated Testing:** Run `php artisan test --filter=ModuleSeederTest`.

#### Child Node Example (`api/config/modules/<root>.php`)
```php
[
    'key' => 'certificate.membership-certificates',
    'name' => 'Membership Certificates',
    'permissions' => [
        config('constants.BASE_PERMISSIONS.MANAGE_MEMBERSHIP_CERTIFICATES') => 'Download and regenerate members\' certificates.',
    ],
],
```

#### Navigation Entry Example (`api/config/navigation/<root>.php`)
```php
[
    'key' => 'appearance.menu',
    'module' => 'appearance.menu',
    'title' => 'Menu',
    'type' => 'basic',
    'link' => '/appearance/menu',
    'permission' => config('constants.BASE_PERMISSIONS.VIEW_APPEARANCE_MENU'),
],
```

---

### UI Coordination Checklist (Reference for Full-Stack Alignment)
The UI treats a key the API never seeded as available. A typo fails silently: the feature simply cannot be switched off. Always copy keys exactly.

1. **Module Key:** Add to `ui/src/app/core/constants/module-keys/<root>.ts`, spelled exactly as in the API's `config/modules/<root>.php` (same file name). A new root gets its own file, spread into `ModuleKeys` in `module-keys/index.ts`.
2. **Top-Level Route:** In `app.routes.ts`, tag the entry with the root key:
   ```typescript
   data: { module: ModuleKeys.JOURNAL }
   ```
3. **Child Routes:** In the feature's `*.routes.ts` / `*.routing.ts`, give every child that is its own sub-module that sub-module's key beside its `permission`:
   ```typescript
   {
       path: 'participants',
       canActivate: [PermissionGuard],
       data: {
           module: ModuleKeys.EVENT_PARTICIPANTS,
           permission: 'view-event-participants',
       },
       component: EventParticipantPanelComponent,
   }
   ```
   *Without this, switching off a sub-module leaves its URL reachable.*
4. **Shell Routes (e.g. `setting.routing.ts`):** Hosting other modules' screens: leave the parent untagged and tag **every** child with the module that owns it. Switching one off then does not take down the whole shell.
5. **Keep Permission Guard:** A module tag does not replace `canActivate: [PermissionGuard]` + `data.permission`.
6. **No Guard Per Route:** `moduleAvailabilityGuard` runs on app shells' `canActivateChild` and checks the route and every ancestor. A tag in `data.module` is sufficient.
7. **Blocks Inside Another Screen:** For elements that no permission covers (a button, panel, or tab), use `*moduleAvailable="moduleKeys.X"`:
   ```html
   <button *moduleAvailable="moduleKeys.EVENT_SUBMISSIONS" (click)="openMySubmissionsDialog()">…</button>
   ```
   *(Content inside `<has-permission>` needs no extra tag, as it already respects module availability).*

---

### Worked Example: Adding "Event Feedback"
A hypothetical new feature under `Event`. Admins view feedback with a permission, members submit feedback while logged in, and the public sees an average rating. All three paths switch off with one module: `event.feedback`.

| Step | File | What to Add |
| :--- | :--- | :--- |
| **Permission** | `api/config/constants.php` | `VIEW_EVENT_FEEDBACK` in `BASE_PERMISSIONS` |
| **Module Node** | `api/config/modules/event.php` | Child `event.feedback` mapping `VIEW_EVENT_FEEDBACK => 'View feedback submitted for an event.'` |
| **Admin Query** | `graphql/event-feedback/*.graphql` | `getEventFeedback` with `@guard` + `@hasPermission` (no `@moduleAvailable`) |
| **Member Mutation** | same | `submitEventFeedback` with `@guard` + `@moduleAvailable(module: "event.feedback")` |
| **Public Query** | `graphql/public/public.query.graphql` | `getPublicEventRating` with `@moduleAvailable(module: "event.feedback")` |
| **Navigation** | `api/config/navigation/event.php` | Entry with `'module' => 'event.feedback'` and its permission |
| **UI Key** | `ui/.../module-keys/event.ts` | `EVENT_FEEDBACK: 'event.feedback'` |
| **UI Route** | `ui/.../event/event.routes.ts` | Child route with `module: ModuleKeys.EVENT_FEEDBACK` + `permission: 'view-event-feedback'` |
| **UI Button** | My Events screen | Submit button wrapped in `*moduleAvailable="moduleKeys.EVENT_FEEDBACK"` |

---

### Common Anti-Patterns & Mistakes

| Mistake | Result |
| :--- | :--- |
| **`@guard` only, no `@moduleAvailable`** | Authenticated users can still execute the feature after it is switched off |
| **Both `@hasPermission` and `@moduleAvailable` on one field** | Creates a duplicate key that drifts from the permission's mapping |
| **UI key misspelled or not seeded** | Treated as available; the switch silently does nothing |
| **Only the top-level route tagged** | Sub-module URLs remain directly reachable when that sub-module is off |
| **Shell parent route tagged** | Switching one module off hides every screen in the shell |
| **Permission mapped under the screen it appears on** | Switching off the owning module does not revoke the permission |
| **Permission or module rows written in a migration** | Bypasses seeders; breaks idempotency and admin overrides |
| **Seeded key renamed** | UI `ModuleKeys` and navigation point at a key that no longer exists |

---

### Review Checklist
- [ ] New permissions are in `config/constants.php` and mapped, with a plain-language description, in **exactly one** module node.
- [ ] New areas have a child node `<parent>.<slug>` (or a new root file under `config/modules/<key>.php`).
- [ ] Every field without `@hasPermission` has `@moduleAvailable(module: "<key>")`.
- [ ] Navigation entries carry `'module' => '<key>'`.
- [ ] No permission, role, navigation, or module rows in migrations (seeders only).
- [ ] UI key added, spelled exactly as in the API.
- [ ] Top-level and sub-module routes tagged; shell children tagged individually.
- [ ] Blocks with no permission wrapped in `*moduleAvailable="moduleKeys.X"`.
- [ ] `ModuleSeederTest` passes; switching the module off blocks nav, routes, UI blocks, and API fields.

