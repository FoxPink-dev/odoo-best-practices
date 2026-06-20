---
name: lint-no-monkey-patch
priority: low
tags:
  - lint
  - monkey-patch
  - inherit
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - override method
  - extend core
  - patch class
---

# lint-no-monkey-patch — Never Monkey-Patch Odoo Core

Monkey-patching Odoo core classes is fragile, breaks on upgrades, and conflicts with other modules. Always use Odoo's official extension mechanisms.

## Incorrect

```python
# Monkey-patching — overrides the method globally
from odoo import models

original_create = models.Model.create
def patched_create(self, vals_list):
    # Custom logic
    return original_create(self, vals_list)

models.Model.create = patched_create
```

## Correct

```python
# my_module/models/sale_order.py
from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        result = super().action_confirm()
        self._my_custom_after_confirm()
        return result
```

## Safe Extension Patterns

| Goal | Correct Approach |
|------|-----------------|
| Add field to existing model | `_inherit` + new field |
| Override method | `_inherit` + `super()` call |
| Add method | Just define it — Odoo merges it in |
| Extend JS component | `patch()` utility from `@web/core/utils/patch` |
| Extend view | `inherit_id` + xpath |
| Intercept RPC call | Inherit controller with `@http.route()` |

## For JavaScript (OWL/legacy)

```javascript
// CORRECT: Use Odoo's patch utility
import { patch } from "@web/core/utils/patch";
import { MyComponent } from "@my_module/my_component";

patch(MyComponent.prototype, "my_module::MyComponent", {
    setup() {
        // Call original
        this._super(...arguments);
        // Add custom logic
        this.myCustomField = useState({ value: 0 });
    },
});
```

## Why

- Monkey-patching modifies global state — affects all modules
- Two modules monkey-patching the same method → one silently wins
- Upgrades overwrite the patched code → breaks silently
- Odoo's `_inherit` and `patch()` are designed for safe extension

## References

- OCA pylint-odoo: https://github.com/oca/pylint-odoo
