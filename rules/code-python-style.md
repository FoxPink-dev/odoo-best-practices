---
priority: MUST
tags: [coding-style, python, pep8]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing Python code for Odoo modules"
    includes: ["*.py", "**/*.py"]
---
# Code Python Style

## Description

Follow PEP8 with Odoo-specific conventions: 4-space indentation, 80-char line limit (soft), lowercase_with_underscore for methods/variables, PascalCase for classes, UPPERCASE for constants. Model names are singular dot-notation (`sale.order`, `res.partner`). Method names use snake_case and describe actions. Avoid wildcard imports. Use one class per file for models.

## Correct

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sales Order'

    name = fields.Char(string='Order Reference', default='/')
    partner_id = fields.Many2one('res.partner', string='Customer')

    def action_confirm(self):
        """Confirm the sales order."""
        self.write({'state': 'sale'})
        return True
```

## Incorrect

```python
# Bad: wildcard import, camelCase method, bad spacing
from odoo import *

class sale_order(models.Model):  # Should be PascalCase
    _name = 'sale.order'

    def confirmOrder(self):  # Should be snake_case
        pass

    Name = fields.Char()  # Should be lowercase
```

## Rationale

Consistent style improves readability and maintainability. PEP8 is the Python standard; Odoo-specific conventions (model naming, method naming) ensure consistency across the ecosystem. Pylint with `pylint-odoo` plugin automatically enforces these rules. One class per file simplifies version control diffs and code navigation.

## References

- PEP8 – Style Guide for Python Code
- Odoo Contributing guidelines: Coding guidelines
- pylint-odoo plugin rules
