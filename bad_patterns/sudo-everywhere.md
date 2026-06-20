---
name: sudo-everywhere
severity: high
tags:
  - anti-pattern
  - security
  - access-rights
---

# sudo() Everywhere

## ❌ Anti-Pattern

```python
def action_view_orders(self):
    orders = self.env['sale.order'].sudo().search([
        ('partner_id', '=', self.partner_id.id)
    ])
    # Bypasses all record rules — user sees ALL orders
```

## ✅ Fix

```python
def action_view_orders(self):
    orders = self.env['sale.order'].search([
        ('partner_id', '=', self.partner_id.id)
    ])
    # Respects ACL and record rules
```

## Why It Hurts

`sudo()` bypasses **all** ACL and record rules. A salesperson using `sudo()` can see every order in the system — including competitor pricing, executive approvals, and other companies' data.

## Safe Uses of sudo()

| Use Case | Justification |
|----------|---------------|
| System operations (cron jobs) | No user context |
| Portal user creating a ticket | User may not have create ACL |
| Migration scripts | Data integrity during upgrade |
| Server-wide notifications | Must reach all users |

## Detected When

- `sudo()` in user-facing controller or button method
- `sudo()` used just to avoid writing proper record rules
- Multiple `sudo()` calls in the same method

## References

- security-record-rules-row-level
- security-least-privilege
