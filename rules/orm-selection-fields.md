---
priority: SHOULD
tags: [orm, selection-fields, fields]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining selection fields"
    includes: ["fields.Selection", "selection="]
  - task: "extending selection values"
    includes: ["selection_add", "ondelete"]
  - task: "dynamic selection"
    includes: ["selection=", "def _selection"]
---
# ORM Selection Fields

## Description

Define selection fields with a static list of `(value, label)` tuples when the options are fixed. Use a callable or method name for dynamic selections that depend on database state or configuration. Use `selection_add` (not redefining the entire `selection` list) when extending a selection field via `_inherit`. Always provide an `ondelete` dict with `selection_add` to define fallback behavior when overriding modules are uninstalled and their options removed.

## Correct

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'

    # Static selection
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('sale', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], default='draft', string="Status")

    # Dynamic selection from a method
    def _selection_product_category(self):
        return self.env['product.category'].search([]).mapped(lambda c: (c.id, c.name))

    product_category_id = fields.Selection(
        selection='_selection_product_category',
        string="Product Category"
    )

# Extension with selection_add
class SaleOrderCustom(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('awaiting_payment', 'Awaiting Payment')],
        ondelete={'awaiting_payment': 'set default'}
    )
```

## Incorrect

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'

    # WRONG: redefining entire selection list instead of using selection_add
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('sale', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('awaiting_payment', 'Awaiting Payment'),
    ])

class SaleOrderCustom(models.Model):
    _inherit = 'sale.order'

    # WRONG: redefining instead of adding — this replaces the original
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('sale', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('awaiting_payment', 'Awaiting Payment'),
    ])
```

## Rationale

The Odoo 17.0 ORM documentation specifies Selection fields: the `selection` attribute "is given as either a list of pairs (value, label), or a model method, or a method name." For inheritance, use `selection_add` which "provides an extension of the selection in the case of an overridden field." The `ondelete` parameter with `selection_add` "provides a fallback mechanism for any overridden field with a selection_add" — this prevents data integrity issues when modules are uninstalled. The `group_expand` option enables dynamic group expansion in read_group results.

## References

- Odoo 17.0 ORM docs: `fields.Selection` — Encapsulates an exclusive choice between values
- Odoo 17.0 ORM docs: `selection` parameter — list of pairs, callable or method name
- Odoo 17.0 ORM docs: `selection_add` — extension of selection in overridden fields
- Odoo 17.0 ORM docs: `ondelete` — fallback mechanism for selection_add options
- Odoo 17.0 ORM docs: `group_expand` — expands read_group results for the field
