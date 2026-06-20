---
name: migrate-idempotent
priority: medium
tags:
  - migration
  - safety
  - idempotent
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - write migration
  - run upgrade
  - re-run script
---

# migrate-idempotent — Make Migration Scripts Idempotent

Migration scripts may run multiple times (failed upgrades, re-runs). Always check existence before creating/altering.

## Incorrect

```python
def migrate(cr, version):
    # CRASH on second run: column already exists
    cr.execute("ALTER TABLE my_table ADD COLUMN new_field varchar")
```

## Correct

```python
def migrate(cr, version):
    _logger.info("Pre-migration: adding new_field")

    # Check column existence
    cr.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'my_table' AND column_name = 'new_field'
    """)
    if not cr.fetchone():
        cr.execute("ALTER TABLE my_table ADD COLUMN new_field varchar")
        _logger.info("Column added")
    else:
        _logger.info("Column already exists — skipping")
```

## Idempotent Operation Patterns

| Operation | Safe Check |
|-----------|-----------|
| Add column | Check `information_schema.columns` |
| Rename column | Check old exists before rename |
| Drop column | Check column exists |
| Create table | `CREATE TABLE IF NOT EXISTS` |
| Add constraint | Check `information_schema.table_constraints` |
| Insert data | Use `ON CONFLICT DO NOTHING` |
| Update data | Always use `WHERE` to scope |

## Full Safety Template

```python
import logging
from odoo.tools import column_exists, table_exists

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    _logger.info("Starting migration from version %s", version)

    # Use Odoo helpers when available
    if not column_exists(cr, 'my_table', 'new_field'):
        cr.execute("ALTER TABLE my_table ADD COLUMN new_field varchar")

    # Or raw SQL checks
    cr.execute("""
        UPDATE my_table
        SET new_field = COALESCE(new_field, old_field)
        WHERE new_field IS NULL AND old_field IS NOT NULL
    """)
    _logger.info("Updated %d rows", cr.rowcount)
```

## Why

- Failed upgrades often require fixing and re-running
- CI pipelines may re-run migration scripts on retry
- Without idempotency, re-running = data loss or crashes

## References

- https://www.postgresql.org/docs/current/infoschema-columns.html
- https://www.odoo.com/documentation/master/developer/reference/upgrades/upgrade_utils.html
