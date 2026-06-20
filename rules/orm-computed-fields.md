---
priority: MUST
tags: [orm, computed-fields, api-depends, store, inverse]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining computed fields"
    includes: ["compute=", "store=True", "@api.depends"]
  - task: "adding inverse methods"
    includes: ["inverse="]
  - task: "adding search methods for computed fields"
    includes: ["def _search_", "search="]
---
# ORM Computed Fields

## Description

Computed fields derive their value from other fields via the `compute` parameter and `@api.depends` decorator. Use `store=True` only when the computed value is frequently read and rarely written (e.g., totals, aggregated counts). Non-stored computed fields are recomputed on every access. Always use `@api.depends` to declare dependencies precisely — avoid over-declaring (triggers unnecessary recomputations) and under-declaring (produces stale values). Provide an `inverse` method when the field should be writable from the UI. Provide a `search` method when the field should be filterable in domains.

## Correct

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.depends('order_line.price_subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.order_line.mapped('price_subtotal'))

    amount_total = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        compute='_compute_amount_total',
        store=True
    )

    # Non-stored computed with inverse
    @api.depends('amount_total', 'currency_id')
    def _compute_amount_total_words(self):
        for record in self:
            record.amount_total_words = self._number_to_words(
                record.amount_total, record.currency_id
            )

    amount_total_words = fields.Char(
        string="Total in Words",
        compute='_compute_amount_total_words',
        store=False
    )
```

## Incorrect

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'

    # WRONG: missing @api.depends - will not recompute automatically
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.order_line.mapped('price_subtotal'))

    amount_total = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        compute='_compute_amount_total',
        store=True
    )

    # WRONG: over-declared dependencies, triggers on any field change
    @api.depends('name', 'partner_id', 'user_id', 'date_order', 'order_line',
                 'order_line.product_id', 'order_line.product_uom_qty',
                 'order_line.price_unit', 'currency_id')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.order_line.mapped('price_subtotal'))
```

## Rationale

The Odoo 17.0 ORM documentation states: computed fields "are computed and returned when requested" and "setting `store=True` will store them in the database and automatically enable searching." The `@api.depends` decorator specifies field dependencies — each argument must be a string with dot-separated field names. Non-stored computed fields are computed on every access, which is fine for lightweight calculations but expensive for heavy ones. Stored computed fields trade write amplification (recomputed on dependency change) for faster reads. The Odoo docs also warn: "precomputing a field can be counterproductive if the records are not created in batch."

## References

- Odoo 17.0 ORM docs: Computed Fields — `compute` parameter, `@api.depends` decorator
- Odoo 17.0 ORM docs: `store=True` — stores computed fields in database
- Odoo 17.0 ORM docs: `inverse` parameter — reverses the computation
- Odoo 17.0 ORM docs: `search` parameter — enables searching on computed fields
- Odoo 17.0 ORM docs: `precompute` — whether field should be computed before insertion
