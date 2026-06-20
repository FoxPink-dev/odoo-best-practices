---
priority: SHOULD
tags: [orm, related-fields, computed-fields, store]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "adding related fields"
    includes: ["related=", "fields\\.\\w+\\(related="]
  - task: "choosing between related and computed"
    includes: ["related=", "compute="]
---
# ORM Related Fields

## Description

Related fields (proxy fields) provide the value of a sub-field on the current record by following a sequence of relational fields. They are a special case of computed fields defined via the `related` parameter. Use `related` when you need read-only access to a field on a related model without writing boilerplate compute methods. Add `store=True` only when the value must be searchable or is read far more often than the source field changes. When the relationship chain involves One2many or Many2many fields (except through a Many2one intermediary), use a custom computed field instead.

## Correct

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Non-stored related — cheap, always current
    partner_email = fields.Char(related='partner_id.email')

    # Stored related — searchable but must be recomputed
    partner_category = fields.Many2many(
        related='partner_id.category_id',
        store=True,
        depends=['partner_id']
    )

    # Cannot use related for this (o2m -> m2m chain)
    partner_all_payments = fields.Many2many(
        'account.payment',
        compute='_compute_partner_all_payments'
    )

    @api.depends('partner_id')
    def _compute_partner_all_payments(self):
        for record in self:
            record.partner_all_payments = record.partner_id.mapped(
                'bank_ids'
            ).mapped('payment_ids')
```

## Incorrect

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # WRONG: Using related for a field that will be heavily searched
    partner_country_name = fields.Char(
        related='partner_id.country_id.name',
        store=False  # cannot search on non-stored related
    )

    # WRONG: related through o2m/m2m — not supported, results not aggregated
    partner_children = fields.Char(related='child_ids.name')
```

## Rationale

The Odoo 17.0 ORM documentation describes related fields as "a special case of computed fields" that provide "the value of a sub-field on the current record." Key properties: by default not stored, not copied, readonly, computed in superuser mode. Add `store=True` to make it stored. The docs explicitly warn: "You cannot chain Many2many or One2many fields in related fields dependencies" — related through a Many2one works, but chaining through o2m/m2m will not aggregate correctly. Use the `depends` parameter on stored related fields to limit recomputation (e.g., `depends=['partner_id']` recomputes only when the relation changes, not when the target field changes).

## References

- Odoo 17.0 ORM docs: Related fields — special case of computed fields
- Odoo 17.0 ORM docs: `nickname = fields.Char(related='user_id.partner_id.name', store=True)`
- Odoo 17.0 ORM docs: Warning about chaining Many2many/One2many in related
- Odoo 17.0 ORM docs: `depends` parameter for stored related fields
