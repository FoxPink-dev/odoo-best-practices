---
priority: SHOULD
tags: [performance, cache, orm, context]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "using with_context or managing cache"
    includes: ["models/*.py"]
---
# Performance Cache Management

## Description

Leverage Odoo's ORM cache: fields are cached per recordset after first read. Use `with_context()` to change environment temporarily without reloading. Clear cache with `invalidate_cache()` when modifying fields outside the ORM (raw SQL). Use `browse()` with IDs already in cache to avoid queries. Be aware that `sudo()` and `with_user()` create new environments that may share cache.

## Correct

```python
# Prefetch all fields at once by accessing on the recordset
partners = self.env['res.partner'].search([('country_id.code', '=', 'BE')])
_ = partners.name  # Triggers prefetch for name on ALL partners in recordset
# Subsequent accesses to name are cache hits
for partner in partners:
    _logger.info(partner.name)  # Cache hit, no query

# with_context to change language without reloading
partner = partner.with_context(lang='fr_FR')
label = partner._get_name()

# Invalidate cache after raw SQL
self.env.cr.execute("UPDATE res_partner SET x_custom = %s WHERE id = %s", [val, partner_id])
self.env['res.partner'].invalidate_cache(['x_custom'], [partner_id])

# Browse from cached IDs
ids = [1, 2, 3]
partners = self.env['res.partner'].browse(ids)  # No query if already cached
```

## Incorrect

```python
# Accessing fields one-by-one defeats prefetching
for partner in partners:
    _logger.info(partner.name)  # First access triggers prefetch for all
    _logger.info(partner.email)  # Second query!
    _logger.info(partner.phone)  # Third query!

# Creating new records instead of reusing from cache
for partner_id in partner_ids:
    partner = self.env['res.partner'].browse(partner_id)
```

## Rationale

The ORM cache stores field values per record. Accessing `record.field` on any record in a recordset triggers a prefetch for that field on ALL records in the prefetch set, but each field is fetched separately. Access multiple related fields on the recordset first (e.g., `partners.name`, `partners.email`, `partners.phone`) to batch them into fewer queries. Use `search_read()` when you need many fields at once.

## References

- Odoo 17.0 ORM docs: "Record cache and prefetching"
- Odoo 17.0 ORM docs: `invalidate_cache()`, `with_context()`
