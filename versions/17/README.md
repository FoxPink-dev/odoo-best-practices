---
name: version-17-owl-dominant
priority: medium
tags:
  - version
  - owl
  - js-framework
odoo_versions:
  - 17
---

# Odoo 17 — OWL Becomes Default

Odoo 17 makes OWL the **default** JavaScript framework. Legacy Widget system is still available but discouraged.

## Key Changes from 16

| Change | 16 | 17 |
|--------|----|----|
| JS default | Legacy + OWL | OWL first |
| `t-esc` | Works | Deprecated, prefer `t-out` |
| View resolution | Priority-based | Same |
| Form view | No changes | Better `@api.onchange` support |

## Important Rules

```javascript
// OWL 2.x — setup() is REQUIRED
class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({ items: [] });
        this.orm = useService("orm");
    }
}
```

## Migration Checklist

- [ ] Replace `Widget.extend()` with `Component` subclasses
- [ ] Use `useService()` instead of importing services directly
- [ ] Add `static template` to all components
- [ ] Move initialization from `start()` to `setup()`
- [ ] Replace `t-esc` with `t-out` in QWeb templates
