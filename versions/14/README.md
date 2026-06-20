---
name: version-14-legacy-widgets
priority: low
tags:
  - version
  - odoo14
  - views
  - legacy
  - owl
odoo_versions:
  - 14
---
# Odoo 14 — Legacy Widgets, Pre-OWL

Odoo 14 is the last version using the legacy JavaScript widget system. OWL exists as an optional addon (`@web/legacy/js/owl`). No OWL templates in core views.

## Key Differences from 15+

| Feature | 14 | 15+ |
|---------|----|-----|
| Frontend | Legacy Widgets | OWL 1.x |
| `@api.one` | ✅ Available | ❌ Removed in 15 |
| `t-esc` | ✅ Only option | `t-out` introduced in 15 |
| OWL | Optional addon | Default in 17 |
| `fields.Command` | ❌ Not available | ✅ New ORM command API |
| View inheritance | `xpath` only | `xpath` + position attributes |

## Legacy Widget Conventions

```javascript
// Odoo 14 — Widget-based component
var FieldWidget = FieldChar.extend({
    template: "MyWidget",
    init: function () { this._super.apply(this, arguments); },
    renderElement: function () { this._super.apply(this, arguments); },
});
```

## Migration Notes (14 → 15)

- Replace `@api.one` with explicit `for rec in self:` loops
- Introduce `t-out` alongside existing `t-esc` (not yet required)
- Test all JS widgets — OWL 1.x is available but not default
- `fields.Command` is new in 15 — don't use in 14 modules

## References

- Odoo 14.0 JavaScript reference: Widget system
- Odoo 14.0 ORM: `@api.one` decorator
- Odoo 15.0 migration guide: Breaking changes from 14
