---
name: knowledge-account-payment
model: account.payment
module: account
priority: medium
---
# account.payment — Payments & Transactions

## Purpose
Records payments (incoming and outgoing) linked to invoices. Supports bank payments, checks, cash, and electronic transfers.

## Key Fields
- `name` — Payment reference
- `payment_type` — Selection: `inbound` (customer pays) | `outbound` (we pay)
- `partner_id` — Many2one to `res.partner`
- `partner_type` — Selection: `customer` | `supplier`
- `amount` — Monetary
- `currency_id` — Many2one to `res.currency`
- `payment_date` — Date
- `state` — Selection: `draft` | `reconciled` | `sent` | `cancelled`
- `payment_method_line_id` — Many2one to `account.payment.method.line`
- `journal_id` — Many2one to `account.journal`
- `destination_account_id` — Many2one to `account.account`
- `reconciled_invoice_ids` — Many2many to `account.move` (paid invoices)
- `move_id` — Many2one to `account.move` (created journal entry)
- `ref` — Char (external reference)
- `communication` — Char (memo / communication)
- `is_matched` — Boolean (fully reconciled)
- `payment_reference` — Char (bank reference)

## Payment Flow
```
draft → [validate] → reconciled
  ↓                       ↓
cancelled ← [cancel] ← cancelled
```

## Common Methods
- `action_post()` — Validate payment, create journal entry
- `action_draft()` — Reset to draft
- `action_cancel()` — Cancel payment
- `_create_payment_entry()` — Generate accounting move
- `_compute_reconciled_invoice_ids()` — Link matched invoices

## Register Payment on Invoice

```python
# Programmatic payment
payment = self.env['account.payment'].create({
    'payment_type': 'inbound',
    'partner_id': invoice.partner_id.id,
    'amount': invoice.amount_residual,
    'payment_date': fields.Date.today(),
    'journal_id': bank_journal.id,
})
payment.action_post()
```

## Known Pitfalls
- `move_id` is created on `action_post()` — don't create moves manually
- Canceling a reconciled payment requires unreconciliation first
- `payment_method_line_id` depends on journal configuration
- Currency conversion happens at `payment_date` rate
- `amount` in company currency — use `currency_id` for multi-currency
