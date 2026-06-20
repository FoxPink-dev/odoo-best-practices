---
name: deploy-config-params
priority: MUST
tags:
  - deploy
  - config
  - parameters
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - configure setting
  - define system parameter
  - make feature configurable
---
# deploy-config-params — `ir.config_parameter` vs Hardcoded Settings

Use system parameters (`ir.config_parameter`) for configuration that must change between environments or after deployment. Hardcode only values that never change.

## Correct

```python
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    max_daily_orders = fields.Integer(
        string="Max Daily Orders",
        config_parameter='my_module.max_daily_orders',
        default=100,
    )

    api_endpoint = fields.Char(
        string="API Endpoint",
        config_parameter='my_module.api_endpoint',
        default='https://api.default.com/v1',
    )
```

```python
# Reading system parameters in business logic
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_daily_limit(self):
        ICP = self.env['ir.config_parameter'].sudo()
        max_orders = int(ICP.get_param('my_module.max_daily_orders', '100'))
        today_orders = self.search_count([
            ('date_order', '>=', fields.Date.today()),
            ('company_id', '=', self.company_id.id),
        ])
        if today_orders >= max_orders:
            raise ValidationError(_("Daily order limit reached."))
```

## Incorrect

```python
# Hardcoded configuration — requires code change to modify
MAX_DAILY_ORDERS = 100
API_ENDPOINT = 'https://api.production.com/v1'

class SaleOrder(models.Model):
    def action_confirm(self):
        if self.env['sale.order'].search_count([]) > MAX_DAILY_ORDERS:
            raise ValidationError("Limit reached")
```

## Rationale

- Environment-specific values (staging vs production URLs, rate limits, timeouts) must never be hardcoded.
- `ir.config_parameter` values are accessible via System Parameters UI and API, and persist across upgrades.
- Always prefix keys with your module name (`my_module.`) to avoid collisions.
- Use `res.config.settings` with `config_parameter` for settings that need a UI.
- Use `sudo()` when reading `ir.config_parameter` because the public user may need access.
- Cache parameters in `@api.depends_context` computed fields when they are read frequently.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/ir_data.html#ir-config-parameter
