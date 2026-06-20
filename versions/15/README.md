---
name: version-15-owl-intro
priority: medium
tags:
  - version
  - owl
  - migration
odoo_versions:
  - 15
---

# Odoo 15 — OWL Introduction Year

Odoo 15 introduces OWL as the new JS framework, but legacy Widget still works. This is the first version where OWL components can be used.

## Key Rules

| Aspect | Detail |
|--------|--------|
| OWL version | OWL 1.x — initial release, limited ecosystem |
| View tag | `<tree>` only, `<list>` not supported |
| JS framework | Legacy + OWL both available |
| Python | Python 3.7+, `dataclasses` available |
| `t-esc` vs `t-out` | Both work; `t-out` introduced |
| `@api.depends` | Context propagation improved |
| Reports | QWeb with `t-esc` (legacy) or `t-out` |
| Search `parent_of` | Available in domain expressions |

## OWL Introduction

```javascript
// Odoo 15 — OWL 1.x available alongside legacy
const { Component, useState, onMounted } = owl;

class MyComponent extends Component {
    setup() {
        this.state = useState({ count: 0 });
        onMounted(() => {
            console.log('mounted');
        });
    }
}
```

## Key Differences from 14

| Change | 14 | 15 |
|--------|----|----|
| OWL | Not available | OWL 1.x (experimental) |
| `t-out` | Not available | New QWeb directive |
| `fields.Command` | Not available | New command API for x2many |
| `parent_of` operator | Not available | New domain operator |
| Search panel | Basic | Enhanced with `searchable` option |
| Many2many tags widget | Basic | Improved with `create_edit` option |

## Common Pitfalls

- OWL 1.x lacks `useService()`; services must be imported manually
- No `props` validation in OWL 1.x — validate manually in `setup()`
- Both Widget and OWL may conflict if mixed in the same view
- `t-out` available but not required; `t-esc` still works everywhere
- No `search_fetch()` — use plain `search()` for prefetching
- Module manifest version format: `'version': '15.0.1.0.0'`

## Migration Notes (14→15)

- Review all JS customizations: consider OWL for new features
- QWeb `t-esc` can stay; migration to `t-out` is optional
- `fields.Command` replaces tuple format `(0, 0, {...})` for x2many
- Search view `<field>` can use `searchable="False"` to exclude from "Search..."
