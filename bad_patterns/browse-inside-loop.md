---
name: browse-inside-loop
severity: critical
tags:
  - anti-pattern
  - orm
  - performance
---

# browse() Inside Loop

## ❌ Anti-Pattern

```python
for partner_id in partner_ids:
    partner = self.env['res.partner'].browse(partner_id)
    name = partner.name
```

## ✅ Fix

```python
partners = self.env['res.partner'].browse(partner_ids)
for partner in partners:
    name = partner.name  # Prefetched in batch
```

## Why It Hurts

`browse(id)` inside a loop = N+1 queries. Odoo's prefetching only works on recordsets, not on single records fetched one at a time.

## Detected When

- `browse(single_id)` inside a for loop
- Collecting IDs in a list then calling `browse()` per item
- `browse(id)` where id comes from a loop variable

## References

- orm-no-n-plus-1
- orm-field-index
