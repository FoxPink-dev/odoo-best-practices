---
priority: SHOULD
tags: [orm, many2many, through-model, relation]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating many2many relationships"
    includes: ["fields.Many2many", "relation="]
  - task: "adding extra fields to M2M"
    includes: ["relation=", "column1=", "column2="]
---
# ORM Many2many Through Models

## Description

Use implicit Many2many tables (no `relation` parameter) for simple many-to-many relationships that need no additional data. When the relationship requires extra fields (e.g., quantity, discount, date), create an explicit through model with `One2many` / `Many2one` fields instead. Explicit through models provide better querying, constraints, and extensibility. When specifying explicit `relation`, `column1`, and `column2` parameters, ensure they are unique per model-comodel pair — the ORM prevents two Many2many fields from using the same implicit relation table.

## Correct

```python
from odoo import models, fields

# Simple M2M (no extra fields) — implicit table is fine
class ProjectTask(models.Model):
    _name = 'project.task'

    tag_ids = fields.Many2many('project.tag', string="Tags")

# Complex M2M with extra fields — explicit through model
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _description = 'Sales Order Line'

    order_id = fields.Many2one('sale.order', string="Order", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price")
    price_subtotal = fields.Monetary(string="Subtotal", currency_field='currency_id')

class SaleOrder(models.Model):
    _name = 'sale.order'

    order_line = fields.One2many('sale.order.line', 'order_id', string="Order Lines")
    product_ids = fields.Many2many(
        'product.product',
        string="Products",
        compute='_compute_products',
        # Using Many2one -> One2many chain instead of direct M2M
    )
```

## Incorrect

```python
from odoo import models, fields

# WRONG: Implicit M2M when extra fields are needed
class SaleOrder(models.Model):
    _name = 'sale.order'

    product_ids = fields.Many2many(
        'product.product',
        string="Products",
        # Cannot store quantity, unit price, or discount on the relation
    )

# WRONG: Two M2M fields with same implicit relation table
class ResPartner(models.Model):
    _name = 'res.partner'

    # ORM will raise error: same comodel, no explicit relation params
    contact_ids = fields.Many2many('res.partner', string="Contacts")
    competitor_ids = fields.Many2many('res.partner', string="Competitors")
```

## Rationale

The Odoo 17.0 ORM documentation specifies: for Many2many, "the attributes `relation`, `column1` and `column2` are optional. If not given, names are automatically generated from model names, provided `model_name` and `comodel_name` are different." The ORM "prevents two many2many fields to use the same relation parameters" unless both use the same model/comodel with explicit parameters, or one belongs to `_auto = False`. For extra data on relations, the Odoo framework conventionally uses explicit through models (like `sale.order.line`) rather than attribute-style M2M, because they support field-level validation, computed fields, and direct querying via `search()` on the through model.

## References

- Odoo 17.0 ORM docs: `fields.Many2many` — relation, column1, column2 parameters
- Odoo 17.0 ORM docs: Implicit relation name generation from model names
- Odoo 17.0 ORM docs: ORM prevents two M2M with same implicit relation params
- Odoo 17.0 ORM docs: `Command` class for M2M manipulation (CREATE, UPDATE, DELETE, etc.)
