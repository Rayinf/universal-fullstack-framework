# Frontend Design Standard

## 1) Goal

Keep all extension modules visually and structurally consistent with the framework baseline.

## 2) Page structure

Use this page skeleton:

1. Page header: title + optional action buttons.
2. Search/filter area.
3. Main table/list area.
4. Pagination area.
5. Dialog/drawer area for create/edit/detail.

## 3) Component consistency

- Prioritize existing shared components before creating new ones.
- Keep form dialogs consistent: same label width strategy, validation placement, and footer buttons.
- Keep table behavior consistent: stripe rows, loading state, empty state, row highlight when needed.
- Keep button priority consistent:
  - primary: create/save/submit
  - default: edit/view
  - danger: delete/destructive actions

## 4) Interaction and feedback

- All async operations must expose loading state.
- All API failures must show user-friendly message and write debug logs.
- Use confirm dialogs before destructive operations.
- Keep success/failure message wording concise and action-oriented.

## 5) Data and typing

- Keep ID fields as string.
- Keep pagination fields and request wrappers unified across modules.
- Keep API response handling consistent with framework wrapper (`code`, `msg`, `data`).

## 6) Visual rules

- Reuse existing spacing, typography, border radius, and color usage from core pages.
- Avoid one-off styles in single pages unless it is a reusable pattern.
- Prefer scoped styles for module-specific rules; keep global styles minimal.

## 7) Extension review checklist

Before merging an extension module, verify:

- Page structure follows baseline skeleton.
- Existing shared components were reused where possible.
- Forms/tables/messages match framework interaction pattern.
- Type-check and build pass.
- New pages do not break router guard/menu behavior.
