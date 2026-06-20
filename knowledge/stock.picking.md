---
name: knowledge-stock-picking
model: stock.picking
module: stock
priority: high
tags:
  - knowledge
  - inventory
  - logistics
---

# stock.picking — Stock Transfer / Delivery Order

## Purpose

Records physical movement of products between locations. Covers deliveries, receipts, internal transfers, and manufacturing orders.

## Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | Char | Reference, auto-generated |
| `partner_id` | Many2one (`res.partner`) | Customer/vendor for delivery |
| `picking_type_id` | Many2one (`stock.picking.type`) | Operation type: delivery, receipt, internal |
| `location_id` | Many2one (`stock.location`) | Source location |
| `location_dest_id` | Many2one (`stock.location`) | Destination location |
| `state` | Selection | `draft` → `confirmed` → `assigned` → `done` → `cancel` |
| `move_ids` | One2many (`stock.move`) | Stock moves — actual product movement |
| `move_lines` | One2many (`stock.move.line`) | Detailed move lines with lot/sn |
| `origin` | Char | Source document reference (e.g., SO number) |
| `scheduled_date` | Datetime | Expected delivery date |
| `date_done` | Datetime | Actual completion date |
| `user_id` | Many2one (`res.users`) | Responsible |

## State Flow

```
draft → confirmed → assigned (stock reserved) → done
                                      → partially_available
                  → cancel (at any point before done)
```

## Key Methods

| Method | Description |
|--------|-------------|
| `action_confirm()` | Confirms picking, creates stock moves |
| `action_assign()` | Reserves stock (assigns moves to quants) |
| `button_validate()` | Completes the transfer |
| `action_cancel()` | Cancels picking, unreserves stock |

## Common Pitfalls

- **`button_validate()` raises if stock insufficient** — handle with proper error feedback
- **Backorders**: partial deliveries create new pickings automatically
- **Location constraints**: source/dest must be valid in the operation type
- **Serial numbers**: require Lot/SN tracking on product
- **Return pickings**: created by reverse transfer, not by editing done pickings

## Common Inheritance

```python
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # Add custom validation before completion
        for picking in self:
            if picking.custom_approval_required:
                raise UserError(_("Approval required before delivery"))
        return super().button_validate()

    def action_confirm(self):
        result = super().action_confirm()
        # Custom post-confirm logic
        return result
```

## References

- orm-no-n-plus-1
- test-transactioncase-default
