---
name: commit-in-business-code
severity: high
tags:
  - anti-pattern
  - orm
  - transaction
---

# cr.commit() in Business Code

## ❌ Anti-Pattern

```python
def action_confirm(self):
    for order in self:
        order.state = 'confirmed'
        self.env.cr.commit()  # Partial commit!
```

## ✅ Fix

```python
def action_confirm(self):
    for order in self:
        order.state = 'confirmed'
    # Automatic commit at end of request
```

## Why It Hurts

`cr.commit()` in business code creates **partial transactions**. If the next record fails, the first records are already committed → data corruption. Odoo commits automatically at the end of a successful request.

## When It's Acceptable

- Long-running batch jobs with progress saving
- Migration scripts processing millions of records
- Never in web request handlers or button actions

## Detected When

- `self.env.cr.commit()`, `cr.commit()`, or `transaction.commit()` in button/controller methods
- Commit inside a loop

## References

- migrate-pre-raw-sql
