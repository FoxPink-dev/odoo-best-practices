---
name: search-inside-loop
severity: critical
tags:
  - anti-pattern
  - orm
  - performance
---

# search() Inside a Loop

## ❌ Anti-Pattern

```python
for order_id in order_ids:
    lines = self.env['sale.order.line'].search([('order_id', '=', order_id)])
    total = sum(lines.mapped('price_subtotal'))
```

## ✅ Fix

```python
lines = self.env['sale.order.line'].search([('order_id', 'in', order_ids)])
grouped = {}
for line in lines:
    grouped.setdefault(line.order_id.id, []).append(line)
```

## Why It Hurts

Each `search()` inside a loop = 1 SQL query. For 1000 orders = 1001 queries vs 1 query.

## Detected When

- `search(...)` or `browse(...)` inside `for`, `while`, or list comprehension
- `search_count()` inside loop

## References

- orm-no-n-plus-1
