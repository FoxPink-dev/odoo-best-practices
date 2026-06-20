---
priority: MUST
tags: [coding-style, decorators, api]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "using Odoo API decorators"
    includes: ["models/*.py"]
---
# Code Decorators

## Description

Use `@api.depends` on computed fields to list all dependencies. Use `@api.constrains` for validation constraints (raise `ValidationError`). Use `@api.onchange` for UI interactions (do NOT write to database inside). Use `@api.model` for methods that don't depend on a specific record. Use `@api.model_create_multi` for `create()` overrides. Use `@api.autovacuum` for cleanup cron methods. Do NOT use the deprecated `@api.one` or `@api.cr`/`@api.cr_uid`/`@api.cr_uid_id_context` (removed in Odoo 14+).

## Correct

```python
from odoo import api, fields, models

class ProductProduct(models.Model):
    _name = 'product.product'

    price = fields.Float()
    tax_id = fields.Many2many('account.tax')
    price_with_tax = fields.Float(compute='_compute_price_with_tax')

    @api.depends('price', 'tax_id')
    def _compute_price_with_tax(self):
        for record in self:
            tax = record.tax_id[:1] if record.tax_id else None
            record.price_with_tax = tax.compute(record.price) if tax else record.price

    @api.constrains('price')
    def _check_price_positive(self):
        for record in self:
            if record.price < 0:
                raise ValidationError(_("Price must be positive."))

    @api.onchange('price')
    def _onchange_price(self):
        if self.price and self.price < 0:
            self.price = 0
            return {'warning': {'title': _("Warning"), 'message': _("Price reset to 0")}}

    @api.model
    def get_default_price(self, product_id):
        product = self.browse(product_id)
        return product.price

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault('name', _("New Product"))
        return super().create(vals_list)
```

## Incorrect

```python
# @api.one is deprecated and removed since Odoo 14
@api.one
def do_something(self):
    pass

# @api.depends missing a dependency
price_with_tax = fields.Float(compute='_compute_price_with_tax')

@api.depends('price')  # Missing 'tax_id'
def _compute_price_with_tax(self):
    pass

# Writing to database in @api.onchange
@api.onchange('field_x')
def _onchange_field_x(self):
    self.write({'field_x': self.field_x * 2})  # WRONG: don't write in onchange
```

## Rationale

`@api.depends` ensures computed fields are correctly invalidated when dependencies change. Missing a dependency produces stale data. `@api.onchange` runs only in the UI (form view); it should never write to DB. `@api.model_create_multi` is the standard for create overrides since Odoo 13, handling multi-record creation properly.

## References

- Odoo 17.0 ORM docs: "Method decorators" section
- Odoo 17.0 ORM docs: `@api.depends`, `@api.constrains`, `@api.onchange`
