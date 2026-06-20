---
priority: MUST
tags: [coding-style, error-handling, exceptions]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "raising or catching exceptions"
    includes: ["*.py"]
---
# Code Error Handling

## Description

Use `UserError` for user-facing validation errors (shown as dialogs). Use `ValidationError` for model constraint violations (raised in `@api.constrains` or `_check_*` methods). Use `AccessError` for security violations. Always wrap user-facing strings in `_(...)` for translation. Catch specific exceptions, never bare `except:`. Clean up resources in `finally` blocks.

## Correct

```python
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo import _

class SaleOrder(models.Model):
    _name = 'sale.order'

    def action_confirm(self):
        if not self.order_line:
            raise UserError(_("Cannot confirm an empty sales order."))
        return super().action_confirm()

    @api.constrains('date_order', 'commitment_date')
    def _check_dates(self):
        for order in self:
            if order.commitment_date and order.date_order > order.commitment_date:
                raise ValidationError(_(
                    "Commitment date must be after order date."
                ))

    def action_validate(self):
        try:
            self._perform_external_check()
        except ExternalAPIError as e:
            raise UserError(_("External validation failed: %s", str(e))) from e
```

## Incorrect

```python
# Bare except catches everything including SystemExit
def action_confirm(self):
    try:
        self._do_something()
    except:
        pass

# UserError for constraint violation (should be ValidationError)
@api.constrains('field_x')
def _check_field_x(self):
    for record in self:
        if record.field_x < 0:
            raise UserError(_("Field X must be positive"))

# No translation wrapper
raise UserError("Cannot confirm order.")
```

## Rationale

`UserError` is caught by the Odoo web client and displayed as a dialog. `ValidationError` is used in Python constraints and SQL constraints for data integrity. Using the right exception type ensures correct UI behavior. Bare `except:` hides bugs (e.g., `KeyboardInterrupt`). Always translate user-visible messages.

## References

- Odoo 17.0 ORM docs: "Error management" section
- `odoo.exceptions` module: `UserError`, `ValidationError`, `AccessError`
