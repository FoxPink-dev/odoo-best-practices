---
name: knowledge-account-move
model: account.move
module: account
priority: high
tags:
  - knowledge
  - accounting
---

# account.move — Accounting Entry (Invoice)

## Purpose

Records all accounting transactions: customer invoices, vendor bills, payments, and journal entries. The central model for the accounting module.

## Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | Char | Move reference / invoice number |
| `move_type` | Selection | `out_invoice` (customer), `in_invoice` (vendor), `entry` (journal), `out_refund`, `in_refund` |
| `partner_id` | Many2one (`res.partner`) | Customer/vendor |
| `invoice_date` | Date | Invoice date |
| `date` | Date | Accounting date |
| `state` | Selection | `draft` → `posted` → `cancel` |
| `invoice_line_ids` | One2many (`account.move.line`) | Invoice lines |
| `amount_untaxed` | Monetary | Subtotal (computed) |
| `amount_tax` | Monetary | Tax (computed) |
| `amount_total` | Monetary | Total (computed) |
| `amount_residual` | Monetary | Amount still due (computed) |
| `payment_state` | Selection | `not_paid`, `in_payment`, `paid`, `partial`, `reversed` |
| `journal_id` | Many2one (`account.journal`) | Required — determines number sequence |
| `currency_id` | Many2one (`res.currency`) | From partner or journal |
| `company_id` | Many2one (`res.company`) | Multi-company isolation |
| `fiscal_position_id` | Many2one (`account.fiscal_position`) | Tax mapping |

## Common Methods

| Method | Description |
|--------|-------------|
| `action_post()` | Posts the move — **irreversible** without reversal |
| `button_draft()` | Resets to draft |
| `_compute_amount()` | Recalculates all amounts |
| `_reverse_moves()` | Creates reversal/credit note |

## Warning: Critical Model

`account.move` is the most sensitive model in Odoo:

- **Never** `sudo()` without absolute necessity
- **Never** modify posted moves directly — use reversal
- **Never** delete accounting entries — use cancel/reversal
- **Always** test invoice flows with `@tagged('post_install', '-at_install')`

## Common Inheritance

```python
class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        # Validate before posting
        self._check_custom_requirements()
        return super().action_post()
```

## Known Pitfalls

- `action_post()` is irreversible — validate before calling
- Tax lines are auto-generated on post; manual tax line edits may be overwritten
- Currency rate is locked at `invoice_date` — changes after posting don't affect the move
- Don't modify `line_ids` directly for invoice lines — use `recompute()` or write through the line model
- `state` field transitions are strictly enforced: `draft → posted → cancel`
- Deleting a posted invoice requires `button_cancel()` first

## References

- test-tags-correct
- security-least-privilege
