---
name: deploy-logging-config
priority: MUST
tags:
  - deploy
  - logging
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - configure logging
  - add logger
  - debug production
---
# deploy-logging-config — Logging Configuration for Production

Use Python's `logging` module with Odoo's logger hierarchy. Production logging must be structured, level-appropriate, and never log sensitive data.

## Correct

```python
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        _logger.info(
            "Order %s confirmed by user %s (company: %s)",
            self.name, self.env.user.login, self.company_id.name,
        )
        # Business logic...
        _logger.debug("Order lines: %s", self.order_line.ids)

    def _sensitive_operation(self):
        _logger.warning(
            "Sensitive operation on order %s by %s",
            self.name, self.env.user.login,
        )
```

**Production config (`odoo.conf`):**
```ini
[options]
log_level = warn
log_handler = my_module:INFO,odoo.tools:WARN
log_db = False
logfile = /var/log/odoo/odoo.log
syslog = False
```

## Incorrect

```python
import logging

_logger = logging.getLogger('my_module')

class SaleOrder(models.Model):
    def action_confirm(self):
        # Logging sensitive data
        _logger.info("Order %s confirmed. Credit card: %s", self.name, self.cc_number)

        # Using print instead of logger
        print(f"Order {self.name} confirmed")

        # F-strings in logging (always evaluated, even if level is suppressed)
        _logger.debug(f"Order details: {self._get_full_details()}")

        # No structured context
        _logger.info("confirmed")
```

## Rationale

- Use `logging.getLogger(__name__)` — Odoo's logger hierarchy maps module paths to log levels in config.
- Production `log_level` should be `warn` or higher. Module-specific levels via `odoo.conf`'s `log_handler`.
- Never log: passwords, API keys, credit cards, PII (personally identifiable information).
- Use lazy formatting: `_logger.info("msg %s", var)` instead of `_logger.info("msg %s" % var)` or f-strings — the string is only formatted if the log level is active.
- Rotate logs via `logrotate` or Docker's logging driver — never let logs grow unbounded.
- Set `log_db = False` in production to avoid logging database errors to the database itself (circular issue).
- Use `_logger.exception()` inside except blocks to capture full tracebacks.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/logging.html
- https://docs.python.org/3/library/logging.html
