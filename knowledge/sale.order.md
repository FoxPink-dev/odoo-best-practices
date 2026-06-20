---
name: knowledge-sale-order
model: sale.order
module: sale
priority: high
tags:
  - knowledge
  - sales
---

# sale.order — Sales Order

## Purpose

Core sales transaction model. Records customer orders, manages order lines, handles pricing, taxes, and order lifecycle (draft → confirmed → done/cancel).

## Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | Char | Order reference, auto-generated via sequence |
| `partner_id` | Many2one (`res.partner`) | Customer — **required**, sets currency, fiscal position |
| `partner_invoice_id` | Many2one (`res.partner`) | Invoice address, defaults from partner |
| `partner_shipping_id` | Many2one (`res.partner`) | Delivery address, defaults from partner |
| `order_line` | One2many (`sale.order.line`) | Line items — core data |
| `amount_untaxed` | Monetary | Subtotal before tax (computed) |
| `amount_tax` | Monetary | Total tax amount (computed) |
| `amount_total` | Monetary | Grand total (computed) |
| `state` | Selection | `draft` → `sent` → `sale` → `done` / `cancel` |
| `date_order` | Datetime | Order date |
| `user_id` | Many2one (`res.users`) | Salesperson |
| `team_id` | Many2one (`crm.team`) | Sales team |
| `company_id` | Many2one (`res.company`) | Multi-company isolation |
| `picking_ids` | One2many (`stock.picking`) | Delivery orders (after confirmation) |
| `invoice_ids` | One2many (`account.move`) | Invoices (after confirmation) |

## Common Methods

| Method | Description |
|--------|-------------|
| `action_confirm()` | Confirms order → creates delivery + invoice |
| `action_cancel()` | Cancels order |
| `action_draft()` | Resets to draft |
| `action_quotation_send()` | Opens email composer |
| `_compute_amount_total()` | Recalculates totals |
| `_prepare_invoice()` | Prepares invoice data |

## Common Inheritance Patterns

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add field
    custom_approval = fields.Boolean()

    # Extend confirm
    def action_confirm(self):
        result = super().action_confirm()
        self._run_custom_approval()
        return result

    # Modify invoice preparation
    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals['custom_field'] = self.custom_field
        return vals
```

## Known Pitfalls

- `action_confirm()` creates stock moves and invoices — test carefully
- `order_line` recomputes `amount_total` via `@api.depends` — avoid N+1
- `partner_id` change resets fiscal position, incoterms, payment terms
- Multi-company: order must be in same company as partner

## References

- module-inherit-never-fork
- orm-no-n-plus-1
