---
name: deploy-env-detection
priority: SHOULD
tags:
  - deploy
  - environment
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - detect environment
  - conditional behavior per env
---
# deploy-env-detection — Environment Detection Patterns

Use `odoo.tools.config` or server environment module (`server_environment`) to detect the current environment instead of ad-hoc checks.

## Correct

```python
from odoo.tools import config


class MyModel(models.Model):
    _name = 'my.model'

    def _get_environment(self):
        """Return 'production', 'staging', or 'development'."""
        return config.get('running_env', 'development')

    def _log_sensitive_data(self):
        if self._get_environment() == 'production':
            _logger.warning("Sensitive operation: %s", self.display_name)
```

```python
# Using server_environment (OCA) for per-environment secrets
# server_environment_files/production/my_module.xml:
# <xml>
#   <my_module>
#     <api_key>prod-secret-key</api_key>
#   </my_module>
# </xml>

from odoo.addons.server_environment import serv_config


class MyApi(models.Model):
    _name = 'my.api'

    def _call_api(self):
        api_key = serv_config.get('my_module', 'api_key')
        # ...
```

## Incorrect

```python
# Hostname-based detection — fragile and non-portable
import socket

HOSTNAME = socket.gethostname()
IS_PRODUCTION = 'prod' in HOSTNAME or HOSTNAME == 'odoo-server-01'

# Hardcoded credentials per environment
if IS_PRODUCTION:
    API_KEY = 'prod-key'
else:
    API_KEY = 'dev-key'
```

## Rationale

- Odoo's `config.get('running_env')` defaults to `'development'` and is set via `--running-env=production` in the config file.
- The OCA `server_environment` module provides per-environment configuration files that can hold secrets outside the codebase.
- Hostname-based detection breaks with container orchestration (Kubernetes, Docker Swarm) where hostnames are dynamic.
- Never hardcode secrets or environment-specific values in Python code.
- Use environment-specific logging levels: verbose in development, warnings-only in production.

## References
- https://www.odoo.com/documentation/18.0/reference/cmdline.html#cmdline-running-env
- https://github.com/OCA/server-env
