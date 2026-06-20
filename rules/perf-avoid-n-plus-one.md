---
priority: MUST
tags: [performance, n-plus-one, prefetching, orm]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "accessing related fields in loops"
    includes: ["models/*.py"]
---
# Performance Avoid N+1 Queries

## Description

Never access relation fields (Many2one, One2many, Many2many) inside a loop over records. The ORM prefetches fields for all records in a recordset, but accessing a relation field on individual records can trigger additional queries per record. Use `mapped()`, `read()`, or `sudo()` on the full recordset before looping to trigger prefetching.

## Correct

```python
# Correct: prefetching works because we access .partner_id on the recordset
# before the loop
order_names = self.env['sale.order'].search([]).mapped('partner_id.display_name')

# Correct: trigger prefetch by accessing the relation on the recordset
orders = self.env['sale.order'].search([('state', '=', 'sale')])
partners = orders.partner_id  # Triggers prefetch of all partners
for order in orders:
    _logger.info('Order %s for %s', order.name, order.partner_id.name)

# Correct: use read() when you need specific fields
data = orders.read(['name', 'partner_id', 'amount_total'])
```

## Incorrect

```python
# Incorrect: N+1 - each iteration fetches partner separately
orders = self.env['sale.order'].search([('state', '=', 'sale')])
for order in orders:
    _logger.info('Order %s for %s', order.name, order.partner_id.name)
    # ^^ triggers individual partner query per loop iteration
```

## Rationale

Odoo's ORM prefetches fields using `_prefetch_ids`: when you access a field on one record, the ORM fetches that field for ALL records in the current prefetch set. However, relation fields may not be in the same prefetch set. Accessing the relation on the full recordset (`orders.partner_id`) triggers a single batch query for all partners. The `mapped()` method also triggers prefetching internally.

## References

- Odoo 17.0 ORM docs: "Record cache and prefetching"
- Odoo 17.0 Performance docs: Query count testing
