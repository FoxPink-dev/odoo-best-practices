---
name: migrate-pre-raw-sql
priority: medium
tags:
  - migration
  - raw-sql
  - pre-migrate
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - write pre-migration
  - rename column
  - schema change
---

# migrate-pre-raw-sql — Pre-Migration Uses Raw SQL Only

Pre-migration scripts run **before** the ORM updates the database schema. The ORM is NOT available — only a raw database cursor.

## Incorrect

```python
# migrations/19.0.1.2.0/pre-migrate.py

def migrate(cr, version):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    # CRASH: env can't work because schema hasn't been updated yet
    records = env['my.model'].search([])
```

## Correct

```python
# migrations/19.0.1.2.0/pre-migrate.py
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    _logger.info("Pre-migration: renaming old_column to new_column")

    # Check if column exists before altering (idempotent)
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'my_table' AND column_name = 'old_column'
    """)
    if cr.fetchone():
        cr.execute("""
            ALTER TABLE my_table
            RENAME COLUMN old_column TO new_column
        """)
        _logger.info("Column renamed successfully")

    # Backup data before dropping a column
    cr.execute("""
        CREATE TABLE IF NOT EXISTS my_table_backup AS
        SELECT id, old_field FROM my_table
    """)
```

## When to Use Pre vs Post

| Phase | ORM? | Schema | Best For |
|-------|------|--------|----------|
| Pre-migration | No | Old schema | Rename columns, backup data, type changes |
| Post-migration | Yes | New schema | Populate new fields, transform data |
| End-migration | Yes | Final | Cross-module fixes |

## Safety Checklist

- Always check column/table existence before altering (idempotent)
- Always backup data before destructive operations
- Always use parameterized queries — never string interpolation
- Log every significant operation for debugging

## Why

- Pre-migration runs before `CREATE TABLE` / `ALTER TABLE` from ORM
- The new model fields don't exist in the database yet
- Using the ORM triggers schema validation against the old schema → crash
- Raw SQL is the only safe option at this stage

## References

- https://www.odoo.com/documentation/master/developer/reference/upgrades/upgrade_utils.html
