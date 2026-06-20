---
priority: MUST
tags: [coding-style, api, classmethod, model-methods]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "choosing between @api.model, @classmethod, or regular method"
    includes: ["models/*.py"]
---
# Code API vs Model

## Description

Use `@api.model` when the method does not depend on a specific record (acts at the model level, like a factory or utility). Use `@classmethod` only for Python-level class operations (e.g., alternative constructors, `_build_model`). Use regular (record) methods for business logic that operates on one or more records. Default to record methods for most business logic. `@api.model_create_multi` is the standard for overriding `create()`.

## Correct

```python
from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = 'sale.order'

    # Record method: acts on a recordset
    def action_confirm(self):
        for order in self:
            order.write({'state': 'sale'})
        return True

    # @api.model: no record needed, acts for the model
    @api.model
    def get_default_terms(self, partner_id):
        partner = self.env['res.partner'].browse(partner_id)
        return partner.property_payment_term_id

    # @api.model: factory method
    @api.model
    def create_empty_order(self, partner_id):
        return self.create({
            'partner_id': partner_id,
            'state': 'draft',
        })

    # @api.model_create_multi: for create overrides
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault('name', self.env['ir.sequence'].next_by_code('sale.order'))
        return super().create(vals_list)

    # @classmethod: rare, for Python-level class operations
    @classmethod
    def _get_ticket_choices(cls):
        return [('normal', 'Normal'), ('priority', 'Priority')]
```

## Incorrect

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    # @api.model used when it's really a record method
    @api.model
    def action_confirm(self):
        # self might be empty recordset - confusing
        self.state = 'sale'

    # @classmethod used unnecessarily
    @classmethod
    def get_default_terms(cls, partner_id):
        # cls() creates empty recordset but loses env context
        partner = cls.env['res.partner'].browse(partner_id)
        return partner.property_payment_term_id
```

## Rationale

Record methods (no decorator) are the most common and expected pattern. They operate on `self` as a recordset. `@api.model` indicates the method can be called on an empty recordset (e.g., from a context-less context). `@classmethod` receives the Python class, not the Odoo model, and loses `self.env` — it should only be used for Python-level operations that don't need ORM access. Incorrect choice leads to confusing code and potential `env` access issues.

## References

- Odoo 17.0 ORM docs: "Method decorators" section
- Odoo 17.0 ORM docs: `@api.model`, `@api.model_create_multi`
