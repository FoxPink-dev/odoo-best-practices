---
priority: MUST
tags: [orm, onchange, api-onchange, computed-fields]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "adding onchange methods"
    includes: ["@api.onchange"]
  - task: "replacing compute with onchange"
    includes: ["onchange", "compute"]
---
# ORM Onchange

## Description

Use `@api.onchange` only for real-time UI feedback that does not affect stored business logic (e.g., dynamic warnings, default values in forms, updating visible fields based on user selection). Prefer computed fields (`@api.depends`) for any logic that must persist or affect stored values — onchanges run only on the client side and are not triggered by server-side writes. Never use `@api.onchange` to set values that must be saved to the database; use `compute` with `inverse` instead. Onchange methods receive a pseudo-record and must not call CRUD methods (`create`, `write`, `unlink`) on it.

## Correct

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_warning(self):
        """Show warning for partners with overdue invoices."""
        if self.partner_id and self.partner_id.has_overdue_invoices:
            return {
                'warning': {
                    'title': "Warning",
                    'message': "This partner has overdue invoices.",
                    'type': 'notification',
                }
            }

    # Business logic that must persist uses computed fields
    @api.depends('order_line.price_subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.order_line.mapped('price_subtotal'))
```

## Incorrect

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # WRONG: onchange for business logic that must persist
    @api.onchange('partner_id')
    def _onchange_partner_compute_total(self):
        total = sum(line.price_subtotal for line in self.order_line)
        self.amount_total = total  # This only updates the form, not the DB!

    # WRONG: calling create/write on a pseudo-record
    @api.onchange('partner_id')
    def _onchange_create_invoice(self):
        self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            # ...
        })
```

## Rationale

The Odoo 17.0 ORM documentation states: @api.onchange "is invoked on a pseudo-record that contains the values present in the form. Field assignments on that record are automatically sent back to the client." Critical warnings: "calling any one of the CRUD methods on the aforementioned recordset is undefined behaviour, as they potentially do not exist in the database yet." And: "@onchange only supports simple field names, dotted names are not supported and will be ignored." For any logic that must be saved, use computed fields with `@api.depends` instead.

## References

- Odoo 17.0 ORM docs: `@api.onchange` — decorates onchange method for given fields
- Odoo 17.0 ORM docs: Warning about CRUD methods on pseudo-records
- Odoo 17.0 ORM docs: Warning about dotted field names in @onchange
- Odoo 17.0 ORM docs: `@api.depends` — specifies field dependencies for compute methods
