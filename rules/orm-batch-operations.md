---
name: orm-batch-operations
priority: critical
tags:
  - orm
  - performance
  - batch
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - bulk update
  - loop create
  - batch delete
  - write many records
---

# orm-batch-operations — Batch Database Operations

Operations on individual records inside loops are slow. Use batch ORM methods that operate on the full recordset.

## Incorrect

```python
# One SQL query per record — terrible for 1000+ records
for order in self.env['sale.order'].search([('state', '=', 'draft')]):
    order.write({'state': 'cancel'})

# One CREATE per iteration
for partner_data in partner_list:
    self.env['res.partner'].create(partner_data)
```

## Correct

```python
# Batch write — one UPDATE query
draft_orders = self.env['sale.order'].search([('state', '=', 'draft')])
draft_orders.write({'state': 'cancel'})

# Batch create — one INSERT with multiple rows
self.env['res.partner'].create([
    {'name': 'Partner A'},
    {'name': 'Partner B'},
    {'name': 'Partner C'},
])

# Batch unlink
self.env['sale.order'].search([('state', '=', 'cancel'), ('date_order', '<', cutoff)]).unlink()
```

## Batch Size Guidelines

| Operation | Recommended Batch | Notes |
|-----------|------------------|-------|
| `create()` | 1000–5000 | PostgreSQL parameter limit |
| `write()` | Full recordset | One UPDATE query |
| `unlink()` | Full recordset | One DELETE query |
| `search()` | 5000–10000 | Use `limit` for pagination |
| Migration scripts | Full dataset | Batch in chunks if memory is tight |

## Chunking for Very Large Datasets

```python
BATCH_SIZE = 2000
offset = 0
while True:
    batch = self.env['sale.order'].search(
        [('state', '=', 'draft')],
        limit=BATCH_SIZE, offset=offset
    )
    if not batch:
        break
    batch.write({'state': 'cancel'})
    offset += BATCH_SIZE
    self.env.cr.commit()  # only in batch jobs, never in web requests
```

## Why

- Each ORM call = minimum 1 SQL query + trigger evaluations + cache invalidation
- Batch operations use single SQL statements with multiple rows
- Looping 10,000 records = 10,000× overhead vs 1 batch call

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
