---
name: version-15-owl-intro
priority: low
tags:
  - version
  - odoo15
  - owl
  - fields-command
  - t-out
odoo_versions:
  - 15
---
# Odoo 15 — OWL 1.x Introduced, t-out, fields.Command

Odoo 15 introduces OWL 1.x as an officially supported frontend framework alongside the legacy widget system. New `fields.Command` API replaces magic tuple syntax for One2many/Many2many operations.

## Key Changes from 14

| Feature | 14 | 15 |
|---------|----|----|
| OWL | Optional addon | First-class support |
| `t-out` | ❌ Not available | ✅ New output directive |
| `fields.Command` | ❌ | ✅ New ORM command API |
| `@api.one` | ✅ | ❌ Removed |
| Many2many tags widget | Widget | OWL component |

## OWL Component Pattern (Odoo 15)

```javascript
// Odoo 15 — First OWL components appear in core
const { Component } = owl;
const { useState } = owl.hooks;

class MyComponent extends Component {
    static template = "my_addon.ComponentName";
    state = useState({ count: 0 });
}
```

## fields.Command API

```python
# Odoo 15+ — use fields.Command instead of magic tuples
from odoo import fields

# Instead of (0, 0, {...}), (1, id, {...}), (2, id), etc.
self.order_line = [
    fields.Command.create({"product_id": product.id, "price_unit": 100}),
    fields.Command.update(line.id, {"price_unit": 120}),
    fields.Command.delete(old_line.id),
]
```

## Migration Notes (14 → 15)

- Replace `@api.one` — Odoo 15 removes it entirely
- Adopt `fields.Command` — old magic tuples still work but deprecated
- Introduce OWL components for new features
- Test legacy widgets for compatibility
- `t-out` available but not yet required alongside `t-esc`

## References

- Odoo 15.0 JavaScript reference: OWL components
- Odoo 15.0 ORM: `fields.Command` API
- Odoo 15.0 release notes: Breaking changes
- owl-t-out-over-t-esc — t-out vs t-esc
