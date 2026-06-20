---
name: deploy-feature-flags
priority: MAY
tags:
  - deploy
  - feature-flags
  - config
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - add experimental feature
  - toggle feature
  - gate functionality
---
# deploy-feature-flags — Feature Toggle Patterns

Use system parameters or config entries as feature flags to toggle experimental, deprecated, or environment-specific features without code deploys.

## Correct

```python
from odoo import api, fields, models
from odoo.tools import config


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _is_feature_enabled(self, feature_key):
        ICP = self.env['ir.config_parameter'].sudo()
        return ICP.get_param(
            f'my_module.feature_{feature_key}',
            config.get(f'my_module.feature_{feature_key}', 'False'),
        ).lower() in ('true', '1', 'yes')

    def action_confirm(self):
        if self._is_feature_enabled('new_pricing_engine'):
            return self._confirm_new_pricing()
        return super().action_confirm()

    def _confirm_new_pricing(self):
        # New logic behind feature flag
        pass
```

```xml
<!-- Enable via System Parameters UI -->
<!-- Key: my_module.feature_new_pricing_engine, Value: True -->
```

## Incorrect

```python
# Comment-based toggling — requires code change to flip
# NEW_PRICING = True  # change to False to disable
NEW_PRICING = True

class SaleOrder(models.Model):
    def action_confirm(self):
        if NEW_PRICING:
            ...
```

## Rationale

- Feature flags allow enabling/disabling functionality without deployments, useful for gradual rollouts, A/B testing, and emergency disabling.
- Three common flag backends (in priority order):
  1. `ir.config_parameter` — runtime toggling via UI (best for production ops)
  2. `odoo.tools.config` — set in config file, ideal for environment-level defaults
  3. Environment variables — for containerized deployments (e.g., Docker secrets)
- Flag naming convention: `module_name.feature_<short_name>` for consistency.
- Remove flags once the feature is stable and the old code path is deleted. Stale flags accumulate technical debt.
- Document the purpose and expected lifetime of each flag.

## References
- https://martinfowler.com/articles/feature-toggles.html
- https://www.odoo.com/documentation/18.0/developer/reference/backend/ir_data.html#ir-config-parameter
