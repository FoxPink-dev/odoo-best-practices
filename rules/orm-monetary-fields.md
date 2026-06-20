---
priority: MUST
tags: [orm, monetary, currency, fields]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining monetary fields"
    includes: ["fields.Monetary"]
  - task: "setting up currency fields"
    includes: ["currency_id", "currency_field"]
---
# ORM Monetary Fields

## Description

Always use `fields.Monetary` instead of `fields.Float` for amounts that represent currency values. Every `Monetary` field must be paired with a `Many2one` field to `res.currency` on the same model, referenced via the `currency_field` parameter (defaults to `'currency_id'`). The ORM uses the linked currency's decimal precision to round and format the value. Storing monetary amounts as bare `Float` fields loses currency context and breaks multi-currency support.

## Correct

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    amount_untaxed = fields.Monetary(string="Untaxed Amount", currency_field='currency_id')
    amount_tax = fields.Monetary(string="Tax", currency_field='currency_id')
    amount_total = fields.Monetary(string="Total", currency_field='currency_id')

    # In an invoice with a different currency field name
    invoice_currency_id = fields.Many2one('res.currency', string="Invoice Currency")
    invoice_amount = fields.Monetary(
        string="Invoice Amount",
        currency_field='invoice_currency_id'
    )
```

## Incorrect

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'

    # WRONG: Float without currency context
    amount_total = fields.Float(string="Total")

    # WRONG: Monetary without a currency field on the model
    amount_total = fields.Monetary(string="Total")

    # WRONG: no currency_field specified, but field is named differently
    total_amount = fields.Monetary(string="Total")  # uses default 'currency_id'
```

## Rationale

The Odoo 17.0 ORM docs define `Monetary` as encapsulating "a float expressed in a given `res_currency`." The `currency_field` parameter defaults to `'currency_id'`. "The decimal precision and currency symbol are taken from the currency_field attribute." Without the `Monetary` type, the system has no way to know the precision rules for the amount — it will use generic float precision, leading to incorrect rounding. The web client uses the `monetary` widget for these fields, which displays the currency symbol and formats according to the currency's decimal places.

## References

- Odoo 17.0 ORM docs: `fields.Monetary` — float expressed in a given res_currency
- Odoo 17.0 ORM docs: `currency_field` parameter — name of the Many2one field holding res_currency
- Odoo 17.0 ORM docs: Default `currency_field = 'currency_id'`
