---
priority: SHOULD
tags: [coding-style, dependencies, injection, architecture]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "designing module dependencies or service classes"
    includes: ["models/*.py", "wizard/*.py"]
---
# Code Dependencies

## Description

Design modules with clear dependency boundaries. Use Odoo's inheritance mechanism to depend on other modules rather than reimplementing functionality. Declare all module dependencies in `depends` in `__manifest__.py`. Use `self.env.ref()` for cross-module record references. Avoid circular dependencies. Use `@api.model` service-like methods for reusable logic.

## Correct

```python
# __manifest__.py
{
    'name': 'Custom Invoicing',
    'depends': ['account', 'sale'],  # Explicit dependencies
}

# models/custom_invoice.py
from odoo import api, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        # Use inherited functionality rather than reimplementing
        result = super().action_post()
        self._send_custom_notification()
        return result

    @api.model
    def get_invoice_summary(self, invoice_ids):
        """Reusable service method accessible from other modules."""
        invoices = self.browse(invoice_ids)
        return {
            'total': sum(invoices.mapped('amount_total')),
            'count': len(invoices),
        }
```

## Incorrect

```python
# Missing 'account' in depends
{
    'name': 'Custom Invoicing',
    'depends': ['sale'],  # Missing 'account'
}

# Reimplementing account logic instead of inheriting
class CustomInvoice(models.Model):
    _name = 'custom.invoice'

    def post_invoice(self):
        # Duplicates Odoo account logic instead of inheriting
        self.state = 'posted'
        self.date = fields.Datetime.now()
```

## Rationale

Odoo's inheritance architecture (`_inherit`) is the dependency injection mechanism. Depending on a module gives access to its models, views, and security rules. Missing `depends` entries cause `NameError` at runtime or broken views. Duplicating logic from other modules creates maintenance burden and diverges from upstream fixes.

## References

- Odoo 17.0 Module Manifest docs: `depends` key
- Odoo development guidelines: Inheritance patterns
