---
name: version-14-saas-classic
priority: medium
tags:
  - version
  - legacy
  - migration
odoo_versions:
  - 14
---

# Odoo 14 — Classic Architecture, Pre-OWL

Odoo 14 is the last version before the OWL transition. All JS is legacy Widget, and the framework is fully Python-classic.

## Key Rules

| Aspect | Detail |
|--------|--------|
| JS framework | Legacy only (`Widget.extend()`, `jQuery`) — no OWL |
| View tag | `<tree>` only, `<list>` not supported |
| Python | Python 3.6+ required, f-strings supported |
| Docker | Requires PostgreSQL 10+ |
| `@api.one` | Already removed (gone since 13) |
| `api.depends` context | `@api.depends('field')` does NOT include context by default |
| Legacy Widget | `web.Widget` is the only component system |
| Reports | QWeb with `t-esc` (not `t-out`) |
| Multi-company | Use `[('company_id', 'in', company_ids)]` in record rules |

## Key Differences from 16+

```python
# Odoo 14 — Manual flush may be needed in some cases
self.env.cr.execute("SELECT ...")  # Raw SQL more common in older code

# Odoo 14 — No search_fetch() yet; use search() + prefetching
records = self.env['res.partner'].search([('active', '=', True)])
```

## Frontend

```javascript
// Odoo 14 — Legacy Widget only
var MyWidget = Widget.extend({
    template: 'MyTemplate',
    start: function () {
        this._super.apply(this, arguments);
        // jQuery DOM manipulation
        this.$('.my-class').on('click', this._onClick.bind(this));
    },
});
```

## Common Pitfalls

- `search_fetch()` does not exist; use plain `search()`
- No OWL components — all custom JS must use `Widget.extend()`
- `t-esc` is the only output directive (`t-out` not yet available)
- No `models.Constraint` — use `_sql_constraints` or `@api.constrains`
- PostgreSQL full-text search (`search_type='trgm'`) not yet available
- Module manifest format: `'version': '14.0.1.0.0'`

## Deprecations Already in Effect

- `@api.one` removed (gone at 13)
- `@api.cr`, `@api.cr_uid`, `@api.cr_uid_id`, `@api.cr_uid_id_context` removed
- `fields.related` with `store=False` on computed — removed in 13, cannot reference compute-less related in 14
