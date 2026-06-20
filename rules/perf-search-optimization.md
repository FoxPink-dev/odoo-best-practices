---
priority: MUST
tags: [performance, search, domain, orm]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing search queries or domains"
    includes: ["models/*.py"]
---
# Performance Search Optimization

## Description

Optimize `search()` calls by: (1) using specific domains that leverage indexes, (2) always passing `limit` when you only need a subset, (3) using `offset` for pagination, (4) avoiding `search([])` (use `search_count` for counts, `search_read` with specific fields), and (5) using `search_count()` instead of `len(search())` when only the count is needed.

## Correct

```python
# Limit when you only need one record
partner = self.env['res.partner'].search([('email', '=', email)], limit=1)

# Use search_count instead of len(search)
count = self.env['sale.order'].search_count([('state', '=', 'draft')])

# Use search_read with specific fields
data = self.env['product.product'].search_read(
    [('sale_ok', '=', True)],
    ['id', 'name', 'list_price'],
    limit=100,
)

# Use domain operators efficiently
records = self.env['res.partner'].search([
    ('category_id', 'in', category_ids),
    ('country_id.code', '=', 'US'),
])
```

## Incorrect

```python
# Loads ALL partners into memory - terrible for large datasets
partners = self.env['res.partner'].search([])
# Then filters in Python
us_partners = partners.filtered(lambda p: p.country_id.code == 'US')

# Counts by loading all records
count = len(self.env['sale.order'].search([('state', '=', 'draft')]))

# No limit on search that returns many results
records = self.env['product.product'].search([('sale_ok', '=', True)])
```

## Rationale

`search([])` loads all records into the ORM cache, consuming memory and time. `filtered()` in Python cannot use database indexes. `search_count` is a single SQL `SELECT COUNT(*)` vs `search()` which loads full records. Always push filtering to the database domain level where indexes apply. Use `search_read` instead of `search` + `read` for a single round-trip.

## References

- Odoo 17.0 ORM docs: "Common ORM methods" / "Search/Read"
- Odoo 17.0 Performance docs: Query optimization
