---
name: lint-api-decorators
priority: low
tags:
  - lint
  - api
  - decorators
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - define model method
  - onchange
  - constrains
  - depends
---

# lint-api-decorators — Use Explicit API Decorators

Always use explicit Odoo API decorators on model methods. They document intent, enable ORM optimizations, and are checked by `pylint-odoo`.

## Incorrect

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    def action_confirm(self):
        # No decorator — ambiguous intent
        ...

    def compute_amount(self):
        # Missing @api.depends — won't auto-recompute
        ...
```

## Correct

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.depends('order_line.price_subtotal', 'order_line.tax_id')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.order_line.mapped('price_tax'))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.fiscal_position_id = self.partner_id.property_account_position_id

    @api.constrains('date_order', 'commitment_date')
    def _check_dates(self):
        for record in self:
            if record.commitment_date and record.commitment_date < record.date_order:
                raise ValidationError(_("Commitment date must be after order date"))

    def action_confirm(self):
        # No decorator needed — regular business method
        ...
```

## Decorator Reference

| Decorator | Purpose |
|-----------|---------|
| `@api.depends('field_a', 'field_b')` | Defines compute trigger dependencies |
| `@api.onchange('field')` | Called when field changes in UI (form view) |
| `@api.constrains('field')` | Validation constraint (raises ValidationError) |
| `@api.model` | Method on model, not recordset |
| `@api.model_create_multi` | Batch create wrapper (Odoo 13+) |
| `@api.returns('model')` | Declares return type for the ORM |

## Why

- `@api.depends` is required for computed fields to auto-recompute
- `@api.constrains` replaces old `_check_*` manual validation
- `@api.onchange` is cleaner than overriding `onchange()` method
- `pylint-odoo` warns when decorators are missing

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
- https://github.com/oca/pylint-odoo
