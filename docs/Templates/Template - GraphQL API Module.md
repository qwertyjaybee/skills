---
title: "API: {{module_name}}"
date: {{date}}
last_modified: {{date}}
tags:
  - api
  - graphql
  - backend
  - laravel
type: api-doc
status: draft # draft | active | deprecated
---

# API Module: {{module_name}}

> [!NOTE] Module Summary
> **Domain:** `{{domain}}`  
> **GraphQL Schema Files:** `api/graphql/{{domain}}/*.graphql`  
> **Primary Models:** `api/app/Models/{{ModelName}}.php`

---

## 1. Schema Definitions

### Queries
```graphql
extend type Query {
  "Fetch {{entity_name}} records with pagination and filtering"
  get{{Entities}}(
    input: Get{{Entities}}Input @spread
  ): {{Entity}}Paginator
    @guard(with: ["cognito"])
    @hasPermission(permission: "{{permission}}")
    @paginate(defaultCount: 15)
}
```

### Mutations
```graphql
extend type Mutation {
  "Create a new {{entity_name}}"
  create{{Entity}}(
    input: Create{{Entity}}Input! @spread
  ): {{Entity}}!
    @guard(with: ["cognito"])
    @hasPermission(permission: "{{permission}}")
    @field(resolver: "App\\GraphQL\\Mutations\\{{Domain}}\\Create{{Entity}}")
}
```

---

## 2. Authorization & Permissions
- **Guards:** Cognito JWT (`cognito`)
- **Required Permission(s):**
  - Read: `{{READ_PERMISSION}}`
  - Create/Update: `{{WRITE_PERMISSION}}`
  - Delete: `{{DELETE_PERMISSION}}`

---

## 3. Business Logic & Error Handling
> [!WARNING] Transaction Safety
> All multi-table mutations must wrap execution in `DB::transaction()` to ensure atomicity.

- **Validation Rules:**
  - Field A: `required`, `string`, `max:255`
  - Field B: `nullable`, `uuid`
- **Audit Logging:** Audited via OwenIt Laravel Auditing if applicable.

---

## 4. Verification & Testing Commands
```bash
docker exec core-aairi-api php artisan test --filter={{TestName}}
docker exec core-aairi-api ./vendor/bin/pint
```

