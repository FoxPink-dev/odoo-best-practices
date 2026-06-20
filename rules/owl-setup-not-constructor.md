---
name: owl-setup-not-constructor
priority: low-medium
tags:
  - owl
  - component
  - lifecycle
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - create owl component
  - extend component
  - initialize state
---

# owl-setup-not-constructor — Use setup() Instead of constructor()

OWL components are classes, but constructors are not overridable in JavaScript. Odoo uses `setup()` as the standard initialization method to allow proper inheritance.

## Incorrect

```javascript
class MyComponent extends Component {
    constructor() {
        super();
        // BAD: constructor can't be overridden by inheriting modules
        this.state = useState({ count: 0 });
        this.loadData();
    }
}
```

## Correct

```javascript
class MyComponent extends Component {
    setup() {
        // GOOD: setup() can be overridden via Odoo's patch utility
        this.state = useState({ count: 0 });
        this.loadData();
    }
}

MyComponent.template = "my_module.MyComponent";
```

## Complete Pattern

```javascript
const { Component, useState, useService, onMounted, onWillUnmount } = owl;

class PartnerList extends Component {
    static template = "my_module.PartnerList";

    static props = {
        categoryId: { type: Number, optional: true },
    };

    setup() {
        this.state = useState({ partners: [], loading: true });
        this.orm = useService("orm");

        onWillStart(async () => {
            this.state.partners = await this.orm.searchRead(
                "res.partner",
                [],
                ["name", "email", "phone"]
            );
            this.state.loading = false;
        });

        onMounted(() => {
            // DOM is ready — safe to access refs
        });

        onWillUnmount(() => {
            // Clean up timers, subscriptions
        });
    }
}
```

## Why

- JavaScript constructors cannot be overridden by Odoo's `patch()` utility
- `setup()` is the official OWL lifecycle hook for initialization
- `setup()` is called after props are set, so `this.props` is available
- Enables clean inheritance and customization across modules

## References

- https://www.odoo.com/documentation/19.0/developer/reference/frontend/owl_components.html
- https://github.com/odoo/owl
