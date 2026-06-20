---
name: orm-field-index
priority: critical
tags:
  - orm
  - performance
  - database
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - add field
  - search domain
  - optimize query
---

# orm-field-index — Index Fields Used in Domains

Fields used in `search()` domain filters, `group_by`, or record rules must have `index=True` for database performance.

## Incorrect

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    custom_code = fields.Char("Custom Code")
    # searched frequently but no index → full table scan
```

## Correct

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    custom_code = fields.Char("Custom Code", index=True)
    status = fields.Selection([
        ('draft', 'Draft'), ('confirmed', 'Confirmed'),
    ], index=True)
    department_id = fields.Many2one('hr.department', index=True)
```

## What to Index

| Field type | When to index |
|------------|---------------|
| Many2one / Foreign Key | Always if used in domains or group_by |
| Selection | If filtered or grouped frequently |
| Char / Text | If used in search or record rules |
| Date / Datetime | If used in date range filters |
| Integer | If used in comparison domains |

## Multi-Column Index

For compound search patterns:

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    _sql_constraints = [
        ('custom_code_company_uniq', 'UNIQUE(custom_code, company_id)',
         'Custom code must be unique per company!'),
    ]
```

## Why

- Unindexed search = full sequential scan on large tables
- Index on foreign keys speeds up JOINs in relational queries
- Record rules with unindexed fields slow down every view load
- PostgreSQL can use multi-column indexes for prefix columns

## References

- https://www.postgresql.org/docs/current/indexes.html
- https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
