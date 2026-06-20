---
name: version-16-owl-legacy
priority: medium
tags:
  - version
  - odoo16
  - owl
  - js-framework
odoo_versions:
  - 16
---

# Odoo 16 — Legacy JS Framework Still Active

Odoo 16 is the **transition version** — both the legacy Widget system and OWL co-exist.

## Key Rules

| Aspect | Detail |
|--------|--------|
| OWL version | OWL 2.x — `useState`, `onMounted` available |
| View tag | `<tree>` only, `<list>` not recognized |
| JS framework | Both legacy (`Widget.extend()`) and OWL work |
| Field decorators | `@api.depends` required on all computed fields |
| Deprecated | `@api.one` removed; use `@api.model` with `for rec in self` |

## Migration Path to OWL

```javascript
// LEGACY (still works in 16, removed in 18+)
var MyWidget = Widget.extend({
    start: function () {
        this._super.apply(this, arguments);
    },
});

// OWL (preferred in 16, required in 18+)
class MyComponent extends Component {
    setup() {
        // ...
    }
}
```

## Common Pitfalls

- `<tree>` is the only valid list tag — don't use `<list>`
- Don't mix Widget and OWL in the same module
- jQuery-based event binding still works but is deprecated
