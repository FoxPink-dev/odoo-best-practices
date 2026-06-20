---
name: knowledge-purchase-order
model: purchase.order
module: purchase
priority: medium
---
# purchase.order — Purchase Orders

## Purpose
Tracks purchases from suppliers: RFQ (Request for Quotation), confirmed PO, receipt, and billing.

## Key Fields
- `name` — Sequence-generated PO reference
- `partner_id` — Many2one to `res.partner` (supplier)
- `partner_ref` — Char (supplier's reference)
- `date_order` — Datetime (order date)
- `date_planned` — Date (expected receipt)
- `date_approve` — Datetime (approval date)
- `state` — Selection: `draft` | `sent` | `to approve` | `purchase` | `done` | `cancel`
- `order_line` — One2many to `purchase.order.line`
- `currency_id` — Many2one to `res.currency`
- `amount_untaxed` — Monetary (computed)
- `amount_tax` — Monetary (computed)
- `amount_total` — Monetary (computed)
- `payment_term_id` — Many2one to `account.payment.term`
- `fiscal_position_id` — Many2one to `account.fiscal.position`
- `picking_count` — Integer (related receipt count)
- `invoice_count` — Integer (related bill count)
- `incoterm_id` — Many2one to `account.incoterms`

## Order Lines (purchase.order.line)
- `product_id` — Many2one to `product.product`
- `name` — Description
- `product_qty` — Float
- `product_uom` — Many2one to `uom.uom`
- `price_unit` — Monetary
- `price_subtotal` — Monetary (computed)
- `date_planned` — Date (line-level receipt date)
- `state` — Selection (inherited from PO header)

## Purchase Flow
```
draft → sent → to approve → purchase → done
                   ↓              ↓
              cancel ← cancel ← cancel
```

## Common Methods
- `button_confirm()` — Confirm PO (draft → purchase)
- `button_approve()` — Approve (to approve → purchase)
- `button_cancel()` — Cancel
- `action_view_invoice()` — Open related bills
- `action_view_picking()` — Open related receipts
- `_prepare_invoice()` — Create bill from PO

## Known Pitfalls
- Don't allow `qty=0` or `qty < 0` on order lines
- `date_planned` is critical for MRP planning
- Canceling a received PO requires returns first
- `purchase.order.line` `state` field is stored from header — use `related` field
