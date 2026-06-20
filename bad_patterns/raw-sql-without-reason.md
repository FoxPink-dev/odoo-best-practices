---
name: raw-sql-without-reason
severity: high
tags:
  - anti-pattern
  - orm
  - security
---

# Raw SQL Without Reason

## ❌ Anti-Pattern

```python
self.env.cr.execute("SELECT id, name FROM res_partner WHERE active = True")
partners = self.env.cr.fetchall()
```

## ✅ Fix

```python
partners = self.env['res.partner'].search([('active', '=', True)])
```

## Why It Hurts

Raw SQL bypasses ORM access control, record rules, translations, cache invalidation, and audit trails. Use it **only** for complex aggregations where the ORM cannot express the query.

## Detected When

- `self.env.cr.execute` or `cr.execute` in business code
- No comment explaining why ORM is insufficient
- Query result used directly instead of mapped to recordsets

## References

- security-never-bypass-orm
