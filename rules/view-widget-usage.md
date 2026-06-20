---
priority: SHOULD
tags: [view, widget]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Add field to form/list view"
    includes: ["views/*.xml"]
---
# Widget Selection Guide

## Description

Choose the correct `widget` for each field type to provide the best UX. The widget attribute transforms how a field is rendered and interacted with.

## Widget Reference

| Field Type | Recommended Widget | Purpose |
|------------|-------------------|---------|
| `many2one` | (default) / `many2one_avatar` | Default dropdown or avatar + name |
| `many2many` / `one2many` | (default) / `many2many_tags` / `many2many_checkboxes` | List / chips / checkboxes |
| `selection` | (default) / `badge` / `radio` / `priority` | Dropdown / colored badge / radio / stars |
| `float` (monetary) | `monetary` | Currency symbol with formatted amount |
| `float` (percentage) | `percentage` / `progressbar` | % display / bar with fill |
| `float` (rating) | `rating` | Star rating interactive widget |
| `integer` (email) | `email` | Mailto link |
| `char` (phone) | `phone` | Click-to-call link |
| `char` (URL) | `url` | Clickable link |
| `char` (image) | `image` / `many2many_image` | Thumbnail display |
| `binary` (image) | `image` | Image preview from binary |
| `text` (HTML) | `html` | Rich text editor (summernote) |
| `date` / `datetime` | `datepicker` / `remaining_days` | Calendar / days-until display |
| `boolean` | `boolean_toggle` | Toggle switch (vs checkbox) |
| `reference` | `reference` / `handle` | Type + value selector |
| `text` (monospace) | `ace` / `json` | Code editor / JSON tree |

## Correct

```xml
<field name="amount_total" widget="monetary"/>
<field name="state" widget="badge" decoration-success="state == 'done'"/>
<field name="priority" widget="priority"/>
<field name="description" widget="html"/>
<field name="partner_id" widget="many2one_avatar"/>
<field name="tag_ids" widget="many2many_tags" color_field="color"/>
<field name="is_active" widget="boolean_toggle"/>
<field name="date_deadline" widget="remaining_days"/>
```

## Incorrect

```xml
<!-- Using plain text for rich content -->
<field name="description"/>

<!-- No monetary widget for money fields -->
<field name="amount_total"/>

<!-- Checkbox provides worse UX than toggle -->
<field name="is_active"/>
```

## Rationale

- The correct widget reduces user errors and improves data entry speed
- `monetary` auto-formats with currency symbol from company settings
- `badge` provides color-coded state visual cues
- `many2one_avatar` shows contact photo + name instead of plain ID
- `many2many_tags` with `color_field` gives colored tag chips
- `boolean_toggle` is more touch-friendly than a checkbox
- `widget="html"` enables rich text editing vs plain textarea

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_records.html
