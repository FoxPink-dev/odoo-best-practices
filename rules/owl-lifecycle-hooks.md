---
name: owl-lifecycle-hooks
priority: low-medium
tags:
  - owl
  - lifecycle
  - hooks
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - fetch data in component
  - dom manipulation
  - cleanup component
---

# owl-lifecycle-hooks — Use Correct OWL Lifecycle Hooks

OWL components have a well-defined lifecycle. Choosing the wrong hook leads to race conditions, memory leaks, or broken UI state.

## Incorrect

```javascript
class PartnerForm extends Component {
    setup() {
        // BAD: fetching data in setup() — blocks first render
        this.partners = await this.orm.searchRead(...);

        // BAD: DOM access in setup() — DOM doesn't exist yet
        const el = document.querySelector('.partner-name');
    }
}
```

## Correct

```javascript
const { Component, useState, useService, onWillStart, onMounted,
        onWillUnmount, onWillUpdateProps, useRef } = owl;

class PartnerForm extends Component {
    static template = "my_module.PartnerForm";

    setup() {
        this.state = useState({ partners: [], loading: true });
        this.orm = useService("orm");
        this.formRef = useRef("formContainer");

        // 1. Fetch data before first render
        onWillStart(async () => {
            this.state.partners = await this.orm.searchRead(
                "res.partner", [], ["id", "name", "email"]
            );
            this.state.loading = false;
        });

        // 2. DOM is ready — attach listeners
        onMounted(() => {
            this.formRef.el.addEventListener("scroll", this._onScroll);
        });

        // 3. React to prop changes
        onWillUpdateProps((nextProps) => {
            if (nextProps.categoryId !== this.props.categoryId) {
                this._reloadData(nextProps.categoryId);
            }
        });

        // 4. Cleanup
        onWillUnmount(() => {
            if (this.formRef.el) {
                this.formRef.el.removeEventListener("scroll", this._onScroll);
            }
        });
    }
}
```

## Hook Reference

| Hook | When | Async? | Use Case |
|------|------|--------|----------|
| `onWillStart` | Before first render | Yes | Fetch initial data |
| `onMounted` | After DOM insertion | No | DOM manipulation, event listeners |
| `onWillUpdateProps` | Before re-render from props | No | Sync derived state from props |
| `onPatched` | After re-render | No | DOM-based side effects |
| `onWillUnmount` | Before DOM removal | No | Cleanup: listeners, timers, subscriptions |
| `onError` | When child throws | No | Error boundary |

## Common Mistakes

1. **Fetching in `setup()`**: Blocks render; use `onWillStart` instead
2. **DOM access in `setup()`**: DOM doesn't exist yet; use `onMounted`
3. **No cleanup in `onWillUnmount`**: Memory leaks from orphaned listeners/timers
4. **Side effects in render**: Use `onPatched` for post-render DOM work

## Why

- Each hook has a specific purpose in the component lifecycle
- Wrong hook causes timing bugs that are hard to reproduce
- Missing cleanup causes memory leaks in long-running sessions

## References

- https://www.odoo.com/documentation/19.0/developer/reference/frontend/owl_components.html
- https://github.com/odoo/owl
