---
priority: SHOULD
tags: [performance, indexes, database]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining model fields or adding indexes"
    includes: ["models/*.py"]
---
# Performance Index Usage

## Description

Add `index=True` on fields that are frequently searched, grouped, or used in domains. Index foreign key fields (Many2one) implicitly in Odoo 17+, but explicitly add indexes for: fields used in `search()`, `order` parameters, `group_by` in `read_group`, and fields in domain conditions. Avoid over-indexing: indexes add write overhead and storage.

## Correct

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _order = 'date_order desc, name'

    name = fields.Char(index=True)  # Searched often
    date_order = fields.Datetime(index=True)  # Used in _order and group_by
    partner_id = fields.Many2one('res.partner', index=True)  # Foreign key
    state = fields.Selection(index=True)  # Filtered frequently
    custom_code = fields.Char(string='Custom Code', index=True)  # Domain searches

    @api.depends('order_line.price_subtotal')
    def _compute_amount_untaxed(self):
        # Indexed fields in compute dependencies are resolved faster
        pass
```

## Incorrect

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    name = fields.Char()  # No index, but searched by name frequently
    state = fields.Selection()  # No index, filtered by domain daily

    # Over-indexing: unnecessary indexes on rarely-queried fields
    internal_note = fields.Text(index=True)
    last_accessed = fields.Datetime(index=True)
```

## Rationale

Database indexes speed up `SELECT ... WHERE` and `ORDER BY` at the cost of slower `INSERT`/`UPDATE`. Fields used in Odoo domains (`[('state', '=', 'done')]`) directly translate to SQL `WHERE` clauses where indexes help. Fields in `_order` become SQL `ORDER BY` and benefit from indexes. Odoo 17+ auto-indexes Many2one fields; for older versions, add explicitly.

## References

- Odoo 17.0 ORM docs: `Field` attributes (`index`)
- Odoo 17.0 Performance docs: Database optimization
