---
priority: MUST
tags: [orm, constraints, sql-constraints, api-constrains]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "adding validation"
    includes: ["@api.constrains", "_sql_constraints", "ValidationError", "raise"]
  - task: "adding uniqueness checks"
    includes: ["unique", "_sql_constraints"]
---
# ORM Constraints

## Description

Use `_sql_constraints` for database-level constraints (unique, check) — they are enforced at the database layer, cannot be bypassed, and are always consistent. Use `@api.constrains` only for Python-level cross-field validation that cannot be expressed in SQL (e.g., comparing multiple fields, calling external services). SQL constraints are preferred for uniqueness and simple checks because they are enforced even during bulk data operations and migrations.

## Correct

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _name = 'product.template'

    name = fields.Char(required=True)
    default_code = fields.Char(string="Internal Reference")
    product_category = fields.Selection([
        ('physical', 'Physical'),
        ('digital', 'Digital'),
    ])

    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)',
         "This internal reference already exists!"),
        ('price_check', 'CHECK(list_price >= 0)',
         "List price must be positive."),
    ]

    @api.constrains('name', 'default_code')
    def _check_name_code(self):
        for record in self:
            if record.name and record.default_code and \
               record.name.lower() == record.default_code.lower():
                raise ValidationError(
                    "Name and Internal Reference must be different."
                )
```

## Incorrect

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _name = 'product.template'

    name = fields.Char(required=True)
    default_code = fields.Char(string="Internal Reference")

    # WRONG: Python constraint for something SQL could enforce better
    @api.constrains('default_code')
    def _check_default_code_unique(self):
        for record in self:
            existing = self.search([
                ('default_code', '=', record.default_code),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError("Default code must be unique!")

    # WRONG: constraint on a field not provided to the method — won't trigger
    @api.constrains('name')
    def _check_name_code(self):
        for record in self:
            if record.name == record.default_code:
                raise ValidationError("Name and code must differ.")
```

## Rationale

The Odoo 17.0 ORM documentation explains `_sql_constraints` as SQL constraints `[(name, sql_def, message)]` and `@api.constrains` as Python constraint checkers. The docs warn: "@constrains only supports simple field names, dotted names are not supported" and "@constrains will be triggered only if the declared fields are included in the create or write call." This means Python constraints can be silently skipped if the field isn't in the values dict. SQL constraints are always enforced regardless of how data enters the database. Use `@api.constrains` only for logic that truly requires Python (cross-field comparison, API calls, date arithmetic).

## References

- Odoo 17.0 ORM docs: `_sql_constraints = []` — SQL constraints [(name, sql_def, message)]
- Odoo 17.0 ORM docs: `@api.constrains` — decorates a constraint checker
- Odoo 17.0 ORM docs: Warning about dotted field names in @constrains
- Odoo 17.0 ORM docs: Warning about fields not present in create/write not triggering @constrains
