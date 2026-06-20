---
name: version-19-new-view-tags
priority: medium
tags:
  - version
  - views
  - breaking-change
odoo_versions:
  - 19
---

# Odoo 19 — New View Tags & OWL 3 Stable

Odoo 19 stabilizes OWL 3 and introduces canonical `<list>` tag.

## Key Changes from 18

| Change | 18 | 19 |
|--------|----|----|
| List view tag | `<tree>` (legacy) | `<list>` (canonical) |
| OWL | 3.x (transition) | 3.x (stable) |
| Form view | Standard | `settings` view enhancements |
| Search view | Standard | `<searchpanel>` improvements |

## New Tag Conventions

```xml
<!-- Odoo 19+ — use <list> -->
<list>
    <field name="name"/>
    <field name="partner_id"/>
    <field name="amount_total" sum="Total"/>
</list>

<!-- Use <tree> only in Odoo ≤ 18 modules -->
```

## Key Rules

| Rule | Details |
|------|---------|
| `<list>` | Required for new modules; `<tree>` still works but deprecated |
| `@api.onchange` | Now works with computed fields in form views |
| `useService()` | All Odoo services migrated to DI pattern |
| `patch()` | Official extension mechanism for JS components |

## Checking Compatibility

```bash
# Scan for deprecated patterns in your codebase
grep -r "<tree" your_module/views/
grep -r "constructor()" your_module/static/
grep -r "_sql_constraints" your_module/models/
```
