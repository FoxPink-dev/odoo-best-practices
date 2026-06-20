---
name: unindexed-foreign-key
severity: medium
tags:
  - anti-pattern
  - orm
  - performance
  - database
---

# Missing Index on Foreign Key

## ❌ Anti-Pattern

```python
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    order_id = fields.Many2one('sale.order', string="Order")
    # No index — slow search by order_id
```

## ✅ Fix

```python
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    order_id = fields.Many2one('sale.order', string="Order", index=True)
```

## Why It Hurts

Unindexed foreign keys cause sequential scans when searching, grouping, or joining on that field. On a table with 500K+ lines, query time goes from milliseconds to seconds.

## Detected When

- Many2one field without `index=True`
- Field used in `search()`, `group_by`, or domain filters
- Slow list views with large datasets

## References

- orm-field-index
