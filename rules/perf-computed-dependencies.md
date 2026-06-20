---
name: perf-computed-dependencies
priority: medium
tags:
  - performance
  - computed-fields
  - api-depends
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - define computed field
  - use api.depends
  - optimize compute
---

# perf-computed-dependencies — Keep @api.depends Chains Short

Deep `@api.depends` chains cause cascading recomputations. Every time a dependency changes, all dependent computed fields must recompute.

## Incorrect

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.depends('order_line.price_subtotal')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = sum(record.order_line.mapped('price_subtotal'))

    @api.depends('subtotal', 'order_line.tax_id.amount')
    def _compute_amount_tax(self):
        for record in self:
            record.amount_tax = ...  # depends on subtotal

    @api.depends('amount_tax', 'subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.subtotal + record.amount_tax
    # Chain: order_line → subtotal → amount_tax → amount_total
    # Changing one line triggers 3 recomputations
```

## Correct

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.depends('order_line.price_subtotal')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = sum(record.order_line.mapped('price_subtotal'))

    @api.depends('order_line.price_subtotal', 'order_line.tax_id.amount')
    def _compute_amount_tax(self):
        for record in self:
            record.amount_tax = sum(
                line.price_subtotal * line.tax_id.amount / 100
                for line in record.order_line
            )

    @api.depends('order_line.price_subtotal', 'amount_tax')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.subtotal + record.amount_tax
    # Independent from subtotal — no cascade
```

## Optimization Tips

| Pattern | Recommendation |
|---------|---------------|
| Deep chain (A→B→C) | Flatten: C depends on A directly |
| Heavy compute | Add `store=True` — compute once on write |
| Per-record compute | Use `for record in self:` with batch prefetching |
| Expensive aggregation | Use `read_group()` inside compute method |

## When to Store

```python
@api.depends('order_line.price_subtotal')
def _compute_subtotal(self):
    for record in self:
        record.subtotal = sum(record.order_line.mapped('price_subtotal'))

# Store when:
# - Read far more often than write
# - Computation is expensive
# - Used in search domains or group_by
# - Used in list view columns (avoids per-row compute)
```

## Why

- Each recomputation triggers a full iteration over the recordset
- Cascading chains multiply the cost: 3 chains = 3× iteration
- Deep chains cause serial recomputation — no parallelization
- Storing breaks the recomputation chain for reads

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
