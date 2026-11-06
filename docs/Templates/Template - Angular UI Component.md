---
title: "UI: {{component_name}}"
date: {{date}}
last_modified: {{date}}
tags:
  - ui
  - angular
  - frontend
  - component
type: ui-doc
status: draft # draft | active | deprecated
---

# UI Component: {{component_name}}

> [!NOTE] Component Details
> **Path:** `ui/src/app/modules/admin/{{path_to_component}}`  
> **Route:** `{{route_path}}`  
> **Module / Standalone:** Standalone Component / Shared Module

---

## 1. Overview & Responsibilities
*Brief description of what this component or view does in the admin application.*

---

## 2. Dependencies & GraphQL Operations
- **GraphQL Queries / Mutations:**
  - `{{QueryName}}GQL`
  - `{{MutationName}}GQL`
- **Shared Components Used:**
  - `app-button`
  - Angular Material Form Controls (`mat-form-field`, `mat-select`, `mat-input`)
  - TipTap Editor (if WYSIWYG rich text is needed)

---

## 3. Form Validation & State Management
> [!IMPORTANT] Angular Material & Reactive Forms Standard
> Always utilize Angular Material form components and Reactive Forms with explicit validators. Avoid raw `<input>` or `[(ngModel)]`.

- **Reactive Form Structure:**
  - `name`: `[null, [Validators.required, Validators.maxLength(100)]]`
  - `email`: `[null, [Validators.required, Validators.email]]`
- **Lifecycle & RxJS Subscriptions:**
  - Unsubscribe strategy: `takeUntil(this._unsubscribeAll)` in `ngOnDestroy()`.

---

## 4. Verification & Testing Commands
```bash
cd /opt/core-aairi/ui
npm run build
npx ng test --include='**/{{component_name}}.component.spec.ts'
```

