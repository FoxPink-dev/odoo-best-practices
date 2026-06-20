---
name: version-18-legacy-removed
priority: medium
tags:
  - version
  - owl
  - breaking-change
odoo_versions:
  - 18
---

# Odoo 18 — Legacy JS Framework Removed

Odoo 18 **removes** the legacy Widget framework entirely. OWL is the only option.

## Breaking Changes from 17

| Change | 17 | 18 |
|--------|----|----|
| Legacy widgets | Available | **Removed** |
| OWL version | OWL 2.x | OWL 3.x |
| Template syntax | `t-out` optional | `t-out` required |
| `_sql_constraints` | String syntax | `models.Constraint` class |
| `attrs` dict | Supported | Prefer direct attributes |

## OWL 3 Changes

```javascript
// OWL 3 removes some deprecated APIs
// BEFORE (OWL 2):
Component.env.bus.on('event', this, this.handler);

// AFTER (OWL 3):
// Use useService('event_bus') instead
const bus = useService('event_bus');
bus.addEventListener('event', this.handler);
```

## Migration Checklist

- [ ] Remove all `Widget.extend()` usage
- [ ] Replace `_sql_constraints` strings with `models.Constraint`
- [ ] Replace `attrs="{'invisible': [('state', '=', 'done')]}"` with direct attributes
- [ ] Ensure all components use `setup()` — not `constructor()`
- [ ] Audit for removed OWL 2.x APIs
