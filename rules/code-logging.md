---
priority: SHOULD
tags: [coding-style, logging, debugging]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "adding logging to Python code"
    includes: ["*.py"]
---
# Code Logging

## Description

Use `logging.getLogger(__name__)` at module level. Use appropriate levels: `DEBUG` for detailed diagnostic info, `INFO` for normal operations (confirmations, state changes), `WARNING` for unexpected but handled situations, `ERROR` for failed operations that don't crash, `CRITICAL` for system-level failures. Never use `print()`. Never log sensitive data.

## Correct

```python
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _name = 'sale.order'

    def action_confirm(self):
        _logger.info("Order %s confirmed by user %s", self.name, self.env.user.name)
        self._check_availability()
        return self.write({'state': 'sale'})

    def _check_availability(self):
        for line in self.order_line:
            if line.product_id.type == 'product' and line.product_id.qty_available < line.product_uom_qty:
                _logger.warning(
                    "Order %s: product %s has insufficient stock (%s < %s)",
                    self.name, line.product_id.name,
                    line.product_id.qty_available, line.product_uom_qty,
                )
```

## Incorrect

```python
# print() has no level control, no module info
print("Order confirmed")

# Using _logger outside the module-level convention
class SaleOrder(models.Model):
    def action_confirm(self):
        import logging
        logging.info("Confirmed")

# String formatting instead of lazy %s
_logger.info("Order " + self.name + " confirmed")

# Logging sensitive data
_logger.info("User password: %s", password)
```

## Rationale

`print()` output goes to stdout, not to Odoo logs, and cannot be filtered by level. Module-level `_logger` (`__name__`) automatically includes the full Python path in log output for easy debugging. Lazy formatting (`%s`) avoids string construction if the log level discards the message. Never log secrets (passwords, API keys, tokens).

## References

- Python `logging` module documentation
- Odoo server logging conventions
