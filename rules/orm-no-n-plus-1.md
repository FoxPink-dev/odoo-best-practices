---
name: orm-no-n-plus-1
priority: critical
tags:
  - orm
  - performance
  - query
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - search records
  - loop over records
  - fetch related fields
---

# orm-no-n-plus-1 — Eliminate N+1 Query Problem

The most common and damaging ORM performance issue: fetching N records triggers N additional queries inside a loop.

## Incorrect

```python
# N+1: one search + N separate queries for partners
orders = self.env['sale.order'].search([('state', '=', 'sale')])
for order in orders:
    partner = order.partner_id  # triggers SQL query per iteration
    partner.email  # another potential query
```

## Correct

```python
# Batch-fetch related records before the loop
orders = self.env['sale.order'].search([('state', '=', 'sale')])
partners = orders.mapped('partner_id')  # single query

# Or use search_read for specific fields
data = self.env['sale.order'].search_read(
    [('state', '=', 'sale')],
    ['name', 'partner_id', 'date_order', 'amount_total']
)
```

## Better

```python
# Odoo prefetches all simple stored fields together
orders = self.env['sale.order'].search([('state', '=', 'sale')])
# Access partner_id with prefetching context
orders.partner_id  # triggers batch fetch for all orders' partners
```

## Why

- Each `for` loop iteration with relational field access = 1 SQL query
- N=1000 records → 1000+ queries instead of 2-3
- Fix often reduces query count by 2-3 orders of magnitude
- Response time drops from tens of seconds to under a second

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
- https://www.odoo.com/event/odoo-experience-2017-692/track/orm-performance-optimizations-and-best-practices-803
