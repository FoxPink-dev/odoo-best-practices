---
name: copy-context-instead-of-propagate
severity: medium
tags:
  - anti-pattern
  - orm
  - context
---

# Copying Context Instead of Propagating

## ❌ Anti-Pattern

```python
def action_open_orders(self):
    ctx = {}  # Fresh context — loses active_id, lang, company
    return {
        'type': 'ir.actions.act_window',
        'context': ctx,
    }
```

## ✅ Fix

```python
def action_open_orders(self):
    ctx = self.env.context.copy()
    ctx.update({'default_partner_id': self.id})
    return {
        'type': 'ir.actions.act_window',
        'context': ctx,
    }
```

## Why It Hurts

Starting from `{}` loses the current environment's language, company, timezone, and active model context. The target view may fail or show wrong data.

## Detected When

- `'context': {}` or `{'key': val}` without propagating `self.env.context`
- Action returns unexpected language or company context

## References

- module-context-propagation
