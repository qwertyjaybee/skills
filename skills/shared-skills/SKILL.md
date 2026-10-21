---
name: shared-skills
description: Shared cross-stack development standards bridging Angular UI and Laravel/Lighthouse API, including upload size limits, permission constants, site constants, and shared component catalogs. Triggers when the user asks for shared cross-stack guidelines or starts their message with /shared-skills or /shared.
---

# Shared UI & API Cross-Stack Standards

## 1. Consistent File & Image Upload Size Limits
Ensure file/image upload size validation limits match exactly between the frontend UI (bytes) and the backend API (kilobytes, e.g., Laravel's `max` validator). Never allow backend limits to diverge from the UI constraints.

- **Image Uploads:** Default to **5MB** (`5 * 1024 * 1024` bytes in UI, `max:5120` kilobytes in backend) or up to **10MB** (`10 * 1024 * 1024` bytes in UI, `max:10240` kilobytes in backend).
- **General File / Document Uploads:** Default to **5MB** or **10MB**.
- **Prompting Rule:** If the file or image upload size limit is unspecified or ambiguous for a given feature, always prompt/ask the user whether to use **5MB** or **10MB** before implementing.

---

## 2. Permission Constants: Single Source of Truth
Permission strings must be defined once as config constants and reused everywhere across the stack (API schemas, resolvers, and UI permission gates).

- **API Config File:** `api/config/permissions.php`
- **Access Pattern in API:** `config('permissions.module_management.view')` → `'view-module-management'`
- **Rule:** Do not hardcode permission string literals directly in GraphQL schema files or UI templates without matching the centralized config definition. Pair backend `@hasPermission` guards with the frontend `<has-permission>` component.

---

## 3. Site Constants (Module Management & Resolvers)
Site constants are part of **Settings → Module management**.
- **Schema Location:** `api/graphql/settings/module-management/site-constants/`
- **Queries:**
  - `getSiteConstants` → `App\GraphQL\Queries\Settings\ModuleManagement\SiteConstants\GetSiteConstants`
  - `getSiteConstantsLight` → `App\GraphQL\Queries\Settings\ModuleManagement\SiteConstants\GetSiteConstantsLight`
  - `getSiteConstantsLevel2ByAliasLevel1` → `App\GraphQL\Queries\Settings\ModuleManagement\SiteConstants\GetSiteConstantsLevel2ByAliasLevel1`
- **Centralization Standard:** Keep resolver logic delegated to a single PHP helper:
  `App\Helpers\SiteConstantsHelper::getLevel2ByAliasLevel1ForAuthenticatedRequest(...)`
- **Status Meanings (`site_constants.active`):**
  - **Level 1 (group):** `0` inactive, `1` active (**admin use**), `2` **public**
  - **Level 2–4:** `0` inactive, `1` active
- **UI Service Layer:** Operations and fragments must be colocated in `const.Gql.ts` files (e.g. `ui/src/app/core/services/settings/module-management/const.Gql.ts`) and consumed by the respective `.service.ts`.

---

## 4. Shared UI Building Blocks Catalog
Before implementing one-off UI logic, reuse building blocks from `ui/src/app/shared/components`:

| Area | Component / Directory | Description |
| :--- | :--- | :--- |
| Actions & Buttons | `button/` | `app-button` (`ButtonComponent`) |
| Permission Gating | `has-permission/` | Wrapper matching backend RBAC |
| Status Badges | `status-badge/` | Standardized status pill |
| Lists & Tables | `table/`, `pagination/` | Enterprise data tables |
| Navigation | `breadcrumb/` | Breadcrumb hierarchy |
| Content Display | `content-items/` | Consistent card/item layout |
| Templates | `template/` | `side-bar-template`, `drawer-template`, `layout-type-3`, `confirmation-modal` |

---

## 5. Module Availability Standards (Cross-Stack Feature Flags)
Every new feature, screen, or permission must declare the module it belongs to, in both the API and the UI, in the same change. Module Management enables administrators to switch entire features off, and that switch strictly overrides role permissions.

### Why Module Mapping Is Mandatory
If a feature is not properly declared in the module tree:
1. Admins cannot switch it off.
2. It continues working even when its parent module is disabled.
3. Its permissions display as `Unassigned` on the Module Management screen.
4. `ModuleSeederTest` fails on permissions lacking module mapping or descriptions.

---

### API Enforcement Standards
The module tree is defined in `api/config/modules/<root>.php` (one file per top-level area). Module keys (e.g. `certificate.types`) form the shared vocabulary between API, UI routes, and navigation.

#### GraphQL Module Check Rules
Each GraphQL field gets **exactly one module check**:
| Field Type / Directive | Module Check Source | Add `@moduleAvailable`? |
| :--- | :--- | :--- |
| **Field with `@hasPermission(...)`** | Permission's module in `api/config/modules/*.php` | **NO** (Never add both) |
| **`@guard` only** (logged-in self-service, e.g. "my membership") | Requires explicit `@moduleAvailable(module: "...")` | **YES** |
| **Public field** (no login / no `@guard`) | Requires explicit `@moduleAvailable(module: "...")` | **YES** |

- **Why `@hasPermission` is sufficient:** `HasPermissionDirective` first checks whether all permissions that could grant access belong to a disabled module. If so, it rejects immediately with *"This module is currently unavailable."* User `hasPermissionTo()` is also overridden to return `false` for disabled modules, meaning `$user->can(...)` checks inside resolvers honor the switch automatically.
- **Never duplicate directives:** Do not put both `@hasPermission` and `@moduleAvailable` on the same field; doing so introduces a redundant key that can drift out of date when permissions are moved.
- **Self-Service / Authenticated Fields:** `@guard` only verifies authentication; it does **not** check module availability. Add `@moduleAvailable`:
  ```graphql
  applyMembership: Message!
    @field(resolver: "App\\GraphQL\\Mutations\\Membership\\Apply")
    @guard(with: ["api"])
    @moduleAvailable(module: "membership.my-membership")
  ```

#### API Implementation Checklist
1. **Permission Constant:** Add each new permission to `config/constants.php` under `BASE_PERMISSIONS` (or `GUEST_PERMISSIONS`).
2. **Map to One Module:** Add it, with a plain-language description, under **exactly one node** in `api/config/modules/<root>.php`. Choose the module that owns the feature, not the screen where it appears.
3. **Child Nodes:** Form child node keys as `<parent.key>.<slug>`. A new top-level area gets its own `api/config/modules/<key>.php`. Never rename or reuse a seeded key. Set `'is_system' => true` only for modules that must never be switched off.
   ```php
   [
       'key' => 'certificate.membership-certificates',
       'name' => 'Membership Certificates',
       'permissions' => [
           config('constants.BASE_PERMISSIONS.MANAGE_MEMBERSHIP_CERTIFICATES') => 'Download and regenerate members\' certificates.',
       ],
   ]
   ```
4. **GraphQL Schema:** Place `@hasPermission` or `@moduleAvailable(module: "<key>")` on every query and mutation.
5. **Navigation:** Every entry in `api/config/navigation/*.php` must include `'module' => '<key>'`:
   ```php
   [
       'key' => 'appearance.menu',
       'module' => 'appearance.menu',
       'title' => 'Menu',
       'type' => 'basic',
       'link' => '/appearance/menu',
       'permission' => config('constants.BASE_PERMISSIONS.VIEW_APPEARANCE_MENU'),
   ]
   ```
6. **Seeders, Never Migrations:** Permissions, roles, role grants, navigation, and modules are written only by seeders (`BasePermissionSeeder`, role seeders, `ModuleSeeder`, `NavigationSeeder`). Migrations are schema-only. `ModuleSeeder` fills in missing definitions and never overwrites admin changes.
7. **Automated Testing:** Run `php artisan test --filter=ModuleSeederTest`.

---

### UI Enforcement Standards
The UI treats any module key the API never seeded as available. Typographical errors fail silently (the feature cannot be switched off). Always copy keys exactly.

#### UI Implementation Checklist
1. **Module Key Constant:** Add it to `ui/src/app/core/constants/module-keys/<root>.ts` matching `api/config/modules/<root>.php` exactly. Re-export in `module-keys/index.ts`.
2. **Top-Level Route:** In `app.routes.ts`, tag the entry with the root key:
   ```typescript
   data: { module: ModuleKeys.JOURNAL }
   ```
3. **Child Routes:** In feature routes (`*.routes.ts` / `*.routing.ts`), tag every sub-module child route with its sub-module key alongside its permission:
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
4. **Shell Routes Hosting Other Modules (e.g. `setting.routing.ts`):** Leave the parent route untagged, and tag every child route with the specific module that owns it. Disabling one module will not disable the entire shell.
5. **Keep Permission Guard:** A module tag does not replace `canActivate: [PermissionGuard]` and `data.permission`.
6. **Do Not Add Guard Per Route:** `moduleAvailabilityGuard` already runs via shell `canActivateChild` and checks the route and all ancestors. A `data.module` tag is sufficient.
7. **UI Blocks Inside Screens Without Permissions:** When a button, panel, or tab has no permission guard, wrap it with `*moduleAvailable="moduleKeys.X"`:
   ```html
   <button *moduleAvailable="moduleKeys.EVENT_SUBMISSIONS" (click)="openMySubmissionsDialog()">...</button>
   ```
   *Note:* Content inside `<has-permission>` does not need `*moduleAvailable` because `<has-permission>` already respects module availability.

---

### Common Anti-Patterns & Mistakes to Avoid
- **`@guard` only without `@moduleAvailable`:** Authenticated users can still execute mutations/queries after the module is turned off.
- **Both `@hasPermission` and `@moduleAvailable` on one field:** Creates duplicate hand-typed keys that drift out of sync when permissions move.
- **Misspelled UI key or unseeded key:** Fails silently; UI treats the module as enabled.
- **Tagging only top-level routes:** Sub-module direct URLs remain accessible even when disabled.
- **Tagging shell parent routes:** Disabling a single sub-module inadvertently disables the entire shell (e.g., Settings).
- **Mapping permission under the screen instead of the owning feature:** Turning off the feature module fails to revoke the permission.
- **Writing permissions/modules in migrations:** Bypasses seeders, breaking idempotency and admin overrides.
- **Renaming seeded keys:** Breaks UI `ModuleKeys` and navigation references.

---

### Review Checklist for New Features / PRs
- [ ] New permissions added to `config/constants.php` and mapped with plain-language descriptions in exactly one node in `api/config/modules/<root>.php`.
- [ ] New feature areas have child node keys in `<parent>.<slug>` format (or a new root file for top-level areas).
- [ ] Every GraphQL field has either `@hasPermission` or `@moduleAvailable(module: "...")`.
- [ ] Navigation entries include `'module' => '<key>'`.
- [ ] Zero permission, role, navigation, or module rows created in migrations (seeders only).
- [ ] UI module key added to `module-keys/<root>.ts` matching the API key exactly.
- [ ] Top-level and sub-module routes tagged; shell route children tagged individually.
- [ ] Screen elements without permissions wrapped with `*moduleAvailable="moduleKeys.X"`.
- [ ] `ModuleSeederTest` passes; toggling the module off in Module Management blocks nav, routes, UI blocks, and API fields.
