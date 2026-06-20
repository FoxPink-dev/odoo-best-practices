---
priority: MUST
tags: [owl, patch, extension, avoid-fork]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "extending Odoo JS components"
    includes: ["**/static/src/**/*.js"]
  - task: "customizing web client"
    includes: ["patch", "extend", "include"]
---
# OWL patch() — Never Fork Odoo JS Modules

## Description

Use `patch()` from `@web/core/utils/patch` to extend or override Odoo's existing JavaScript components. Forking (copying the entire file) breaks on upgrades and prevents other modules from patching the same component. `patch()` is the official extension mechanism for Odoo's web client.

## Correct

```javascript
import { patch } from "@web/core/utils/patch";
import { SaleOrderLine } from "@sale/...";

patch(SaleOrderLine.prototype, "my_module::SaleOrderLine", {
    computeTotal() {
        const total = this._super(...arguments);
        return total + this.adjustment;
    },
});
```

## Incorrect

```javascript
// WRONG: Forking — copying the entire SaleOrderList component
// and modifying it directly. Lost on next Odoo update,
// conflicts with other modules.
import { Component } from "@odoo/owl";

class CustomSaleOrderList extends Component {
    // Entire original code pasted here with one modification
    // ...
}
```

## Rationale

`patch()` is the officially supported extension mechanism in Odoo 16+. It uses the `_super()` pattern (similar to Python's `super()`) to call the original method. A patched method can be further patched by other modules. Forking creates an unmaintainable copy that must be manually updated on every Odoo upgrade and breaks when other modules try to extend the same component.

## References

- Odoo 17.0 JavaScript reference: `@web/core/utils/patch`
- Odoo 18.0 OWL reference: Module extension patterns
- Odoo 19.0: patch() as the canonical extension API
