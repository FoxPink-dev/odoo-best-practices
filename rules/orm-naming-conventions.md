---
priority: MUST
tags: [orm, models, fields, naming]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating a new model"
    includes: ["class.*models.Model", "class.*models.TransientModel", "class.*models.AbstractModel"]
  - task: "adding fields"
    includes: ["fields.", "_name", "_description", "_rec_name"]
  - task: "reviewing model definitions"
    includes: ["_name\\s*=", "_inherit", "_inherits"]
---
# ORM Naming Conventions

## Description

Odoo model names use singular dot-notation reflecting the module's business domain (e.g., `sale.order`, `res.partner`, `stock.move`). Field names use snake_case with descriptive, non-abbreviated names. Consistent naming ensures discoverability, avoids conflicts, and follows the framework's established patterns.

## Correct

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sales Order'

    name = fields.Char(string="Order Reference")
    partner_id = fields.Many2one('res.partner', string="Customer")
    order_line = fields.One2many('sale.order.line', 'order_id', string="Order Lines")
    currency_id = fields.Many2one('res.currency', string="Currency")
    amount_total = fields.Monetary(string="Total", currency_field='currency_id')
    is_expedited = fields.Boolean(string="Expedited Delivery")
    delivery_date = fields.Date(string="Expected Delivery Date")
```

## Incorrect

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.orders'          # WRONG: plural model name
    _description = 'sale orders'   # WRONG: lowercase description

    ord_name = fields.Char(string="Order Reference")           # WRONG: abbreviated field name
    prt_id = fields.Many2one('res.partner', string="Customer") # WRONG: abbreviated field name
    order_lines = fields.One2many('sale.order.line', 'order_id') # WRONG: no string attr
    tot_amt = fields.Monetary(string="Total")  # WRONG: abbreviated and no currency_field
    isExpedited = fields.Boolean(string="Expedited")  # WRONG: camelCase field name
```

## Rationale

Model names in dot-notation with singular nouns are the Odoo convention established since version 8.0. The ORM automatically generates the database table name by replacing dots with underscores (e.g., `sale_order` for `sale.order`). Plural model names break the convention and confuse developers. The `_description` should be a human-readable capitalized string (used in UI titles). Field names must be snake_case to comply with PEP8 and Odoo's own style; camelCase or abbreviated names reduce readability. The `string` parameter provides the user-visible label; omitting it makes the ORM capitalize the field name automatically, which may produce awkward labels.

## References

- Odoo 17.0 ORM docs: Models section — `_name` is the model name in dot-notation, module namespace
- Odoo 17.0 ORM docs: `_description` is the model's informal name
- Odoo 17.0 ORM docs: Fields — `string` is the label; if not set the ORM takes the field name capitalized
- PEP8 naming conventions
