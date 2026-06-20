---
name: module-inherit-never-fork
priority: critical
tags:
  - module
  - inheritance
  - upgrade-safety
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - inherit model
  - extend model
  - customize core
---

# module-inherit-never-fork — Always Use _inherit

Zero modifications to Odoo core modules. Every customization must be a separate module that extends via `_inherit`, field definitions, and view overlays.

## Incorrect

```python
# Directly modifying odoo/addons/sale/models/sale_order.py
# → Lost on upgrade, breaks git history, no other module can override
```

## Correct

```python
# my_module/models/sale_order.py
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_field = fields.Char("Custom Field")

    def action_confirm(self):
        result = super().action_confirm()
        self._my_custom_logic()
        return result
```

## Three Inheritance Mechanisms

| Type | `_inherit` | `_name` | `_inherits` | Table |
|------|-----------|---------|-------------|-------|
| Class | Set | Omitted | - | Same table |
| Prototype | Set | New name | - | New table |
| Delegation | - | New name | `{parent: 'field_id'}` | Both tables |

## Why

- Core modifications are overwritten on every Odoo upgrade
- Prevents other modules from also extending the same model
- Violates Odoo's modular architecture
- Private API usage (`_` prefixed methods) breaks across versions

## References

- Odoo ORM docs: https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
- OCA guidelines
