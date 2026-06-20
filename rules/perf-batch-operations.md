---
priority: MUST
tags: [performance, batch, bulk-operations, orm]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "processing multiple records or bulk data"
    includes: ["models/*.py", "wizard/*.py"]
---
# Performance Batch Operations

## Description

Process records in batches instead of one-by-one. Use `search_read()` for reading specific fields from many records, `read_group()` for aggregated data, `browse()` with record IDs, `create()` with multi-record lists, `write()` with a dict for all records, and `unlink()` on recordsets. Avoid looping over large recordsets for individual field access.

## Correct

```python
# Batch create
lines_data = [
    {'product_id': p.id, 'product_uom_qty': 10}
    for p in products
]
self.env['sale.order.line'].create(lines_data)

# search_read for specific fields
data = self.env['product.product'].search_read(
    [('type', '=', 'product')],
    ['id', 'qty_available', 'virtual_available'],
)

# read_group for aggregations
group_data = self.env['sale.order'].read_group(
    [('state', '=', 'sale')],
    ['amount_total', 'partner_id'],
    ['partner_id'],
)

# Batch write
records.write({'state': 'done'})
```

## Incorrect

```python
# Individual creates in a loop
for p in products:
    self.env['sale.order.line'].create({
        'product_id': p.id,
        'product_uom_qty': 10,
    })

# Individual reads in a loop
total = 0
for order in orders:
    total += order.amount_total

# Individual writes in a loop
for rec in records:
    rec.state = 'done'
```

## Rationale

Each `create()` call is a separate SQL `INSERT`. Looping for reads triggers individual SQL queries (N+1). `read_group()` translates to a single `GROUP BY` query. Batch `write()` sends one `UPDATE` for the whole recordset. The ORM optimizes batch operations through its cache and prefetching; individual operations bypass these optimizations.

## References

- Odoo 17.0 ORM docs: `create()`, `write()`, `unlink()`, `search_read()`, `read_group()`
- Odoo coding guidelines: Performance section
