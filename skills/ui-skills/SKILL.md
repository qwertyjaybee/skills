---
name: ui-skills
description: Comprehensive Angular UI engineering guidelines, component architecture, form validation, WYSIWYG editor standards, shared templates, typography, and UI defensive standards. Triggers when the user asks for UI/Angular guidelines or starts their message with /ui-skills or /ui.
---

# Angular UI Development Standards

## 1. Architecture & Component Standards
- **Change Detection & Structure:** Default to `ChangeDetectionStrategy.OnPush` unless Signals or architecture dictate otherwise. Prefer Standalone components.
- **File Structure:** Split components into `.component.ts`, `.component.html`, and `.component.scss` (or `.css` if legacy) under `ui/src/app/modules/…`. Services under `*.service.ts`.
- **GraphQL Documents:** Colocate query/mutation/fragment strings in `const.Gql.ts` files under the same feature or service directory.
- **Subscriptions & Memory Management:** Manage RxJS subscriptions using the `async` pipe or `takeUntilDestroyed()`. DO NOT subscribe inside component constructors or use manual `Subject`/`ngOnDestroy` boilerplate. All component-level subscriptions (dialog closures, mutation triggers, preview requests) must pipe `takeUntilDestroyed()`.
- **Debounced Search & Async Race Condition Defense:**
  - When debouncing search terms via a `Subject` or control `valueChanges`, ALWAYS switch onto the API call stream using `switchMap` instead of nesting an unswitched/untracked `.subscribe()` inside the stream. Nested inner subscriptions create race conditions where older in-flight requests can resolve after newer requests, resulting in stale data overwriting the latest search.
  - Cancel previous in-flight requests automatically with `switchMap(() => this._fetchItems().pipe(catchError(() => of(null))))`.
  - Always pair with `distinctUntilChanged()`, `takeUntilDestroyed()`, and extract reusable data-fetching/applying helper methods (e.g. `_fetchItems()`, `_applyItems()`) shared across search streams, pagination changes, and delete/reload handlers.
- **Placement of New Code & Imports:**
  - Append new methods, functions, variables, inputs, outputs, and properties to the **last part / bottom** of their respective class section or file.
  - Append new `import` statements at the **bottom / last part** of the imports block, never at the top.
- **Component Class Organization & Section Banners (Clean Code & Easy Maintenance):**
  To ensure enterprise maintainability and readability across complex Angular components, organize `.component.ts` classes into clear, logical sections separated by standard 3-line comment banners:
  ```typescript
  // =========================================================================
  // <Section Title>
  // =========================================================================
  ```
  **Standard Member Ordering & Structure:**
  1. `Injected Services`: Modern `inject(...)` tokens (`DestroyRef`, `BreakpointObserver`, `Router`, etc.).
  2. `View Children`: `@ViewChild` and `@ViewChildren` queries.
  3. `Inputs & Outputs`: `@Input()` and `@Output()` properties.
  4. `State: <Category>`: Categorize component state into focused, single-purpose groups:
     - `State: Hierarchy & Layout` (or `State: Layout & UI Controls`) (`isCompact`, `hierarchyOpen`, `hierarchyCollapsed`)
     - `State: Loading & Operation Flags` (`isLoading`, `loadFailed`, `isReordering`, `isEditing`, `isCreating`)
     - `State: Data & Permissions` (`membershipTiers`, `user_permissions`)
     - `State: Form & Media` (`form!: FormGroup`, `iconFile`, `iconPreview`, `removeIcon`)
     - `State: Insertion & Pagination` (`targetInsertIndex`, `pageSizeOptions`, `pagination`)
  5. `Constructor & Lifecycle`: `constructor(...)`, `ngOnInit()`, `ngAfterViewInit()`. Subscriptions managed via `pipe(takeUntilDestroyed(this.destroyRef))`.
  6. `Permission & Capability Helpers`: Role/capability checks (`canCreate()`, `canEdit()`, `canArchive()`) and lightweight boolean getters.
  7. `Domain-Specific Method Groups`: Group component methods cleanly by domain responsibility (e.g., `Hierarchy Navigation & Drawer Control`, `Form Management & Submission`, `Data Fetching & Subscriptions`, `Dialog & Modal Handlers`, `Drag & Drop / Reordering Handlers`, `Utility Helpers`).
  When adding new properties or methods to an organized component, place them inside their corresponding designated section rather than scattering them arbitrarily.
- **Ownership:** Compute ownership (e.g. `isOwner`) in parent feature components and pass down via `@Input()`. Only presentational child components should avoid injecting `AuthService`.
- **Button Component (`app-button`):**
  - Location: `ui/src/app/shared/components/button/button.component.ts` (Selector: `app-button`, Standalone: `true`).
  - Use for primary actions instead of raw `<button mat-button>` to ensure consistent icons, roles, and layout.
  - Inputs: `button_material_type` (`'mat-flat-button' | 'mat-icon-button'`), `button_role` (`'view' | 'update' | 'archive' | 'delete' | 'drawer-close' | 'Add' | 'return'`), `button_text`, `material_color`, `mat_tooltip`, `is_disabled`, `icon_placement`, styling hooks (`button_css`, `text_css`, `icon_css`).
  - Output: `callback` — parent handles the click.
  - If creating a custom button, follow the outline design pattern.
- **Shared Templates:**
  - Located under `ui/src/app/shared/template/` (`side-bar-template/`, `drawer-template/`, `layout-type-3/`, `confirmation-modal/`).
  - Prefer these templates for new screens to align spacing, typography, and controls.

---

## 2. Permissions in UI (`has-permission`)
- Use the shared wrapper `ui/src/app/shared/components/has-permission/` (selector: `has-permission`) so UI visibility matches backend authorization.
  ```html
  <has-permission [permissions]="['view-module-management']">
    <!-- content only for authorized users -->
  </has-permission>
  ```
- Inputs:
  - `permissions`: String array of permission names to check.
  - `match`: `true` (default: user must have ALL permissions) or `false` (ANY permission).
  - `hideWhileLoading`: Hide content while permissions are loading (default `true`).
  - `enableAnimation`: Optional fade-in when allowed.

---

## 3. WYSIWYG Editor Standards (`app-wysiwyg-editor`)
- **JSON Format Requirement:** Always configure `[outputFormat]="'json'"` when integrating `app-wysiwyg-editor`.
- **TipTap Persistence:** Store and persist rich text content in TipTap JSON format (`stringified` JSON) rather than raw HTML.
- **Rendering JSON:** Render stored JSON using the shared `tiptapHtml` pipe:
  ```html
  <div [innerHTML]="content | tiptapHtml"></div>
  ```
- **Paste Prevention & Sanitization:** When images or tables are excluded from an editor's toolbar or feature requirements, strictly reject and prevent pasting them via clipboard events:
  - Intercept native `paste` and `drop` events on the editor container.
  - Reject direct image files, image MIME data transfer items, and HTML containing `<img>` tags or base64 data URLs.
  - If tables are disallowed, convert table structures into clean paragraph text or strip table tags before insertion rather than allowing raw `<table>` DOM elements.
  - Strip disallowed inline styles (colored text, background colors, highlights, font sizes) to preserve consistent typography.

---

## 4. UI Typography & Overflow Containment Defenses
Always anticipate long unbroken text strings, concatenated slugs/identifiers, and URLs:
- **Mandatory Word Break Rules:**
  - **Never use `break-all` on prose or user-written text paragraphs:** `break-all` (`word-break: break-all`) forces text to break between any two arbitrary characters even within normal words (e.g., breaking "description" into "descrip-" and "tion" mid-line), creating broken, unnatural reading.
  - **Correct Defense Pattern:** Use Tailwind `break-words [overflow-wrap:anywhere]` (or `overflow-wrap: anywhere; word-break: normal;`):
    - Normal words with spaces will break cleanly at standard word boundaries.
    - Long unbroken continuous strings (e.g. `descriptiondescription...` without spaces or long URLs) will safely wrap anywhere to prevent container blowout.
  - Apply `break-words [overflow-wrap:anywhere]` to dynamic user-facing text containers, headings (`h1-h6`), paragraphs, quotes, card content, table cells, and links.
- **Flexbox & Grid Intrinsic Sizing Defenses:** When text is rendered inside a flex item or CSS grid column, always add `min-width: 0` (or Tailwind `min-w-0`). Without `min-w-0`, the default CSS `min-width: auto` prevents flex/grid children from shrinking below the intrinsic width of an unbroken string, leading to container overflow and horizontal blowout.
- **Sidebar & List Items Text Containment:** For master-detail sidebars, search lists, and data cards, all parent flex wrappers and paragraph containers must have `min-w-0` and `flex-1` alongside `break-words [overflow-wrap:anywhere]` so continuous non-spaced strings never exceed the sidebar width or push action buttons off-screen.
- **Justified Text Safety:** When using `text-align: justify`, do not set `overflow-wrap: normal` or `word-break: normal`. Always pair with `overflow-wrap: break-word; word-break: break-word; hyphens: auto;`.

---

## 5. Forms, Validation & Modals
- **Angular Forms & Material Controls Over Legacy HTML Forms:**
  - **No Legacy HTML Form Elements:** Never use unmanaged, plain HTML form elements (e.g., raw `<input>`, `<select>`, `<textarea>`) or legacy HTML form wrappers.
  - **Always Use Angular Material Controls:** All text inputs, textareas, and select dropdowns must be wrapped in `<mat-form-field>` using Angular Material components:
    - Text and numeric inputs: `<input matInput [formControlName]="..." />`
    - Textareas: `<textarea matInput [formControlName]="..." rows="..."></textarea>`
    - Dropdowns: `<mat-select [formControlName]="..." placeholder="...">` with `<mat-option [value]="...">`
    - Searchable dropdowns: Embed `<ngx-mat-select-search>` within `<mat-select>`.
    - Checkboxes and Radios: Use `<mat-checkbox>` and `<mat-radio-group>` / `<mat-radio-button>`.
  - **Reactive Forms Requirement:** Bind form fields to Reactive Forms (`FormGroup`, `FormControl`, `FormArray`) using `[formControlName]` or `[formControl]`. For standalone filter controls where reactive forms are not in use, bind via Angular `[(ngModel)]` or `[value]` + `(selectionChange)` on Angular Material controls, never raw HTML selects.
- **Modal Close on Escape Key:** Ensure that any created modal, dialog, or drawer can be dismissed/closed when the Escape (`Esc`) key is pressed.
- **Angular Material Error Messaging (`mat-error`):**
  - Always pair form controls inside `mat-form-field` with explicit, user-friendly `<mat-error>` elements.
  - Bind error displays to specific form validation states (e.g., `formGroup.get('fieldName')?.hasError('required')`, `email`, `minlength`, `maxlength`).
  - Ensure error messages match the exact underlying validator bounds (e.g. if `maxLength(125)` is enforced, the error message must state 125 characters, not 50 or 200).
  - Ensure error messages render cleanly without breaking field alignment, pushing layout bounds, or clipping text.
- **Numeric & Decimal Input Precision:**
  - Standard `<input type="number">` parsers strip extra decimal zeros (such as converting `0.0000` to `0`), allowing inputs with illegal decimal precision to silently bypass Angular `Validators.pattern`.
  - For strict fixed decimal amounts (e.g. monetary rates capped at 2 decimal places), prefer `<input matInput type="text" inputmode="decimal">` paired with a custom validator (`AbstractControl` validator) that verifies both string representation and regex boundaries.
  - Convert values safely to numbers in the submission payload before sending to backend GraphQL APIs.
- **Dynamic List Item Duplicate Prevention:**
  - When users dynamically add items to an array/list (such as requirements, privileges, tags), always check for duplicates case-insensitively and trimmed before appending to the form control.
  - If a duplicate entry is detected, abort addition and display an informative error toast (e.g., via `ToastrService`) identifying the duplicated item.
- **Scrollable Dynamic Lists & CDK Drop Lists:**
  - Dynamic user-editable lists (e.g., `cdkDropList`) must specify a maximum height with vertical overflow (e.g., `max-h-[300px] overflow-y-auto`) so adding many items does not push surrounding layout containers or form action footers off screen.
  - In Angular CDK `@for` loops, always declare the index explicitly (e.g., `@for(item of items; track $index; let i = $index)`) so delete or action buttons pass the exact item index (`i`) rather than deleting index `0` due to an undefined index variable.
- **UI Freeze & Autocomplete Safety:**
  - Bind RxJS `valueChanges` subscriptions with `takeUntilDestroyed()` to prevent memory leaks across modal instances.
  - Reset controls asynchronously (`setTimeout(() => control.setValue('', { emitEvent: false }), 0)`) inside selection callbacks to avoid synchronous event loop deadlocks.
  - Trap inner observable errors with `catchError(() => of(null))` inside `switchMap` so API failures never break the outer stream.
- **Image & Icon Fallback Placeholders:**
  - Always provide an explicit placeholder icon (such as `feather:check-square` or an appropriate SVG icon) whenever an image, avatar, tier logo, or step icon is missing, null, empty, or fails to load.
  - Render placeholders in a clean neutral container (`bg-white` with border/shadow) rather than leaving an empty void or broken image.
- **Character Limit Enforcement & Counter Display (Inputs & Textareas):**
  - **Hard Input Boundary:** Every input or textarea in a modal, drawer, or page must enforce a maximum character limit using the native `maxlength="N"` attribute on the `<input>` or `<textarea>`. This ensures the input stops accepting characters and prevents additional input once the limit is reached.
  - **Bottom-Right Character Counter Indicator:** Always indicate the current character count and maximum limit outside the box at the bottom right.
    - Inside Angular Material `<mat-form-field>`: Use `<mat-hint align="end">{{ form.get('controlName')?.value?.length || 0 }}/N</mat-hint>` (or template ref `#fieldInput` with `{{ fieldInput.value.length || 0 }}/N`).
    - For standalone/custom input containers outside `mat-form-field`: Position a counter label at the bottom right outside the input box (e.g., using `flex justify-end` or absolute positioning `text-right text-xs text-gray-400 mt-1`).
  - **Validation Synchronization:** Always pair `maxlength="N"` with Angular's reactive form validator `Validators.maxLength(N)` and an explicit `<mat-error>` if applicable to ensure full form status and UX parity.
- **Template Method Binding Prevention:** Do not bind heavy layout/convergence calculations inside template loops (`*ngFor` or `@for`). Cache/memoize these properties on changes to avoid CPU degradation on Angular change detection cycles.
