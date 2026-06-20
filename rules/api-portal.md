---
priority: SHOULD
tags: [api, portal, controller, website]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify portal controller"
    includes: ["controllers/*.py", "views/*.xml"]
---
# Portal Controller Patterns

## Description

Portal controllers extend `portal` user experience. Inherit from `odoo.addons.portal.controllers.portal.CustomerPortal` and use `@http.route()` with `auth='user'` and type `'http'`. Always check `request.uid` for authentication and use `request.env.user` for portal-specific logic.

## Correct

```python
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class PortalOrder(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'order_count' in counters:
            values['order_count'] = request.env['sale.order'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
            ])
        return values

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_orders(self, page=1, sortby=None, filterby=None, **kw):
        domain = [('partner_id', '=', request.env.user.partner_id.id)]
        order_count = request.env['sale.order'].search_count(domain)
        pager = portal_pager(
            url='/my/orders',
            total=order_count,
            page=page,
            step=self._items_per_page,
        )
        orders = request.env['sale.order'].search(
            domain, limit=self._items_per_page, offset=pager['offset']
        )
        values = {
            'orders': orders,
            'page_name': 'order',
            'pager': pager,
            'default_url': '/my/orders',
        }
        return request.render('sale.portal_my_orders', values)

    @http.route(['/my/order/<int:order_id>'], type='http', auth='user', website=True)
    def portal_order_detail(self, order_id, **kw):
        order = request.env['sale.order'].browse(order_id)
        if order.partner_id != request.env.user.partner_id:
            return request.redirect('/my')
        return request.render('sale.portal_order_detail', {'order': order})
```

## Incorrect

```python
from odoo import http
from odoo.http import request

# Not inheriting from CustomerPortal — missing portal features
class MyPortal(http.Controller):

    @http.route(['/my/models'], type='http', auth='public', website=True)
    def list_models(self):
        # No partner check — anyone can see all records
        records = request.env['my.model'].sudo().search([])
        return request.render('my_module.template', {'records': records})
```

## Rationale

- Inheriting `CustomerPortal` provides `_prepare_home_portal_values`, `_items_per_page`, pager integration
- Always scope domains to `request.env.user.partner_id` for record privacy
- Use `website=True` for portal routes to enable website layout wrapping
- Validate ownership on detail pages — never trust `order_id` from URL alone
- `portal_pager` provides consistent pagination across all portal pages
- Portal controllers should render templates (type='http'), not return JSON

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html
