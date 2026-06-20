---
priority: SHOULD
tags: [api, webservice, integration]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Design web service API for external integration"
    includes: ["controllers/*.py", "services/*.py"]
---
# Web Service API Design Patterns

## Description

Design web services as dedicated controller classes under `/api/*` routes with consistent JSON envelopes, error handling, versioning, and authentication. Use `type='json'`, always return structured responses, and implement request validation.

## Correct

```python
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError


class OrderAPI(http.Controller):

    @http.route('/api/v1/orders', type='json', auth='user', methods=['GET'], csrf=False)
    def list_orders(self, offset=0, limit=80, **kw):
        domain = []
        if kw.get('state'):
            domain.append(('state', '=', kw['state']))
        total = request.env['sale.order'].search_count(domain)
        orders = request.env['sale.order'].search(domain, offset=offset, limit=limit)
        return {
            'count': total,
            'results': orders.read(['name', 'partner_id', 'amount_total', 'state']),
        }

    @http.route('/api/v1/orders/<int:order_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_order(self, order_id):
        order = request.env['sale.order'].browse(order_id)
        if not order.exists():
            return {'error': 'NOT_FOUND', 'message': _('Order not found')}
        return {'data': order.read(['name', 'partner_id', 'amount_total', 'state'])[0]}

    @http.route('/api/v1/orders', type='json', auth='user', methods=['POST'], csrf=False)
    def create_order(self, **kwargs):
        required = ['partner_id', 'order_line']
        for field in required:
            if field not in kwargs:
                return {'error': 'VALIDATION', 'message': _('Missing required field: %s') % field}
        try:
            order = request.env['sale.order'].sudo().create(kwargs)
            return {'id': order.id, 'name': order.name}
        except Exception as e:
            return {'error': 'CREATION_FAILED', 'message': str(e)}

    @http.route('/api/v1/orders/<int:order_id>/action', type='json', auth='user', methods=['POST'], csrf=False)
    def action_order(self, order_id, action):
        order = request.env['sale.order'].browse(order_id)
        if not order.exists():
            return {'error': 'NOT_FOUND', 'message': _('Order not found')}
        if action == 'confirm':
            order.action_confirm()
        elif action == 'cancel':
            order.action_cancel()
        else:
            return {'error': 'INVALID_ACTION', 'message': _('Unknown action: %s') % action}
        return {'success': True, 'state': order.state}
```

## Incorrect

```python
from odoo import http
from odoo.http import request

# No API versioning, no error handling, inconsistent response format
class BadAPI(http.Controller):

    @http.route('/orders/list', type='http', auth='public', csrf=False)
    def list(self):
        orders = request.env['sale.order'].sudo().search([])
        return str([(o.id, o.name) for o in orders])
```

## API Design Checklist

| Concern | Recommendation |
|---------|---------------|
| Versioning | Prefix routes with `/api/v1/`, `/api/v2/` |
| Auth | Use API keys via `auth='user'` or custom `auth='api_key'` |
| Format | Always return JSON with `{'data': ...}` or `{'error': code, 'message': ...}` |
| Errors | Consistent error envelope with machine-readable codes |
| Pagination | Support `offset`/`limit` params, return `count` + `results` |
| Methods | Use correct HTTP verbs: GET (read), POST (create), PUT (update) |
| Writing | `sudo()` is typically needed for API writes to bypass UI restrictions |
| Validation | Validate required fields before creating records |
| Rate limit | Consider `ir.config_parameter` for API rate limits |

## Rationale

- Version prefix (`v1`, `v2`) allows backward-compatible API evolution
- Consistent JSON envelopes make client-side error handling predictable
- Field validation returns clear errors before attempting creation
- `sudo()` for API writes ensures external integrations work without UI-specific constraints
- Pagination prevents unbounded result sets from slowing the API
- Dedicated action endpoints (`/<id>/action`) are safer than exposing all methods

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html
