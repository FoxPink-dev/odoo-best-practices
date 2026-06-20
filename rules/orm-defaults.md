---
priority: SHOULD
tags: [orm, defaults, default, default_model, _defaults]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "setting field defaults"
    includes: ["default=", "lambda self:", "_default_", "default_get"]
  - task: "context-based defaults"
    includes: ["default_", "context", "get_default"]
---
# ORM Defaults

## Description

Set field default values using the `default` parameter directly on the field definition — either as a static value or a callable (function or lambda). Use `default_get()` override for complex default logic that depends on context. Use context keys with `default_` prefix for passing defaults from actions, views, and other models. Never use the deprecated `_defaults` dictionary attribute (removed in Odoo 13+). For defaults that depend on other field values, use `@api.onchange` or computed fields instead.

## Correct

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'

    # Static default
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('sale', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], default='draft')

    # Callable default — function reference
    date_order = fields.Datetime(default=fields.Datetime.now)

    # Callable default — lambda for computed default
    user_id = fields.Many2one(
        'res.users',
        string="Salesperson",
        default=lambda self: self.env.user
    )

    # Override default_get for context-dependent defaults
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'company_id' in fields_list and 'allowed_company_ids' in self.env.context:
            res['company_id'] = self.env.context['allowed_company_ids'][0]
        return res
```

## Incorrect

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'

    # WRONG: deprecated _defaults (removed since Odoo 13)
    _defaults = {
        'state': 'draft',
        'user_id': lambda self: self.env.user,
    }

    # WRONG: mutable object as default (shared across records)
    tag_ids = fields.Many2many('sale.tag', default=[(4, 1)])

    # WRONG: callable without lambda/function — evaluates at class load time
    date_order = fields.Datetime(default=fields.Datetime.now())
```

## Rationale

The Odoo 17.0 ORM documentation explains: default values are "defined as parameters on fields, either as a value: `name = fields.Char(default='a value')` or as a function called to compute the default value." The `default_get()` method is the API for returning default values and is called during record creation. The context-based mechanism (`context={'default_field_name': value}`) is how views and actions pass default values to child records. The deprecated `_defaults` class attribute was removed in Odoo 13.0. Mutable defaults (empty list, empty dict) should use a lambda to create a new instance per call, not a shared reference. `fields.Datetime.now` (without parentheses) is a function reference; `fields.Datetime.now()` with parentheses evaluates at class definition time.

## References

- Odoo 17.0 ORM docs: Field defaults via `default` parameter
- Odoo 17.0 ORM docs: `name = fields.Char(default="a value")`
- Odoo 17.0 ORM docs: `name = fields.Char(default=lambda self: self._default_name())`
- Odoo 17.0 ORM docs: `default_get(fields_list)` returns default values
