---
priority: MUST
tags: [api, controller, http, route]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify HTTP controller"
    includes: ["controllers/*.py"]
---
# Web Controller Best Practices

## Description

Controllers expose HTTP endpoints. Use `@http.route()` decorator with explicit `type`, `auth`, `methods`, and `csrf` parameters. Follow the naming convention: one controller class per file under `controllers/`, importing from `odoo.http`.

## Correct

```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    @http.route('/my/model/<int:record_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_model_data(self, record_id):
        record = request.env['my.model'].browse(record_id).sudo()
        if not record.exists():
            return {'error': 'NOT_FOUND', 'message': 'Record not found'}
        return {'data': record.read(['name', 'state'])[0]}

    @http.route('/my/model/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_model(self, **kwargs):
        record = request.env['my.model'].sudo().create(kwargs)
        return {'id': record.id}
```

## Controller Naming Convention

```python
# File: controllers/my_model.py

from odoo import http
from odoo.http import request


class MyModelController(http.Controller):
    ...
```

## Incorrect

```python
from odoo import http

class MyController(http.Controller):

    @http.route('/my/model/list', auth='public')
    def get_all(self, **kwargs):
        # No auth check, no type declaration, no CSRF
        records = http.request.env['my.model'].search([])
        return str(records)
```

## Route Design Guidelines

| Parameter | Recommendation |
|-----------|---------------|
| `auth` | `'user'` for authenticated, `'public'` only if intentionally open |
| `type` | `'json'` for API, `'http'` for web pages |
| `methods` | Always specify HTTP methods explicitly |
| `csrf` | `False` for JSON APIs, `True` (default) for web forms |
| `cors` | Set if the endpoint is called from external domains |

## Rationale

- Explicit `auth` prevents accidental public access
- JSON type returns structured data; HTTP type returns rendered templates
- CSRF protection prevents cross-site request forgery on form submissions
- Method restriction (GET/POST) follows REST conventions
- `sudo()` should be used carefully and only for cross-model access
- Always validate record existence before returning data

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html
