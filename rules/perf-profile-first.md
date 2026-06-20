---
name: perf-profile-first
priority: medium
tags:
  - performance
  - profiling
  - debugging
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - slow query
  - optimize performance
  - debug
---

# perf-profile-first — Profile Before Optimizing

Never guess about performance. Use Odoo's built-in tools to identify real bottlenecks before applying optimizations.

## Profiling Tools

### 1. Odoo Server Profiler

```bash
# Enable SQL logging
odoo-bin --log-sql

# Or in odoo.conf
[options]
log_sql = True
```

### 2. PostgreSQL EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT id, name FROM sale_order
WHERE state = 'sale'
ORDER BY date_order DESC;
```

### 3. Odoo Profiler from Code

```python
import logging
_logger = logging.getLogger(__name__)

@api.model
def search(self, domain, **kwargs):
    from odoo.tools import profile
    with profile():
        return super().search(domain, **kwargs)
```

### 4. PGStat Statements

```sql
SELECT query, calls, total_time, rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 20;
```

## Common Bottlenecks

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Slow list view | Complex record rules | Simplify domain, add indexes |
| Slow form view | Computed fields with N+1 | Batch compute, add `store=True` |
| Slow import | Per-record validation | Batch validation logic |
| High CPU | No indexes on search fields | Add `index=True` |

## Why

- Most performance issues are caused by a few specific queries
- Blind optimization adds complexity without measurable benefit
- Profiling tells you exactly which queries are slow and why
- Measure before and after to verify improvement

## References

- https://www.postgresql.org/docs/current/sql-explain.html
- Odoo Experience 2017: ORM Performance talk
