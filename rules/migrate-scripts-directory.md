---
name: migrate-scripts-directory
priority: medium
tags:
  - migration
  - upgrade
  - scripts
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - create migration script
  - upgrade module
  - change schema
---

# migrate-scripts-directory — Migration Script Structure

When module data models change (rename fields, change types, restructure data), migration scripts tell Odoo how to transform existing data automatically during `-u module_name`.

## Correct Directory Layout

```
my_module/
└── migrations/
    └── 19.0.1.2.0/          # version from __manifest__.py
        ├── pre-migrate.py    # runs BEFORE schema update
        ├── post-migrate.py   # runs AFTER schema update
        └── end-migrate.py    # runs after ALL modules updated
```

## Script Signatures

### pre-migrate.py (raw SQL only — ORM is not ready)

```python
def migrate(cr, version):
    """Rename column before schema update."""
    cr.execute("""
        ALTER TABLE my_table
        RENAME COLUMN old_name TO new_name
    """)
```

### post-migrate.py (ORM is available)

```python
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    records = env['my.model'].search([])
    for record in records:
        record.status = 'active' if record.old_field else 'draft'
```

## Version Numbering

```
'version': '19.0.1.2.0'
#          ^^^ ^ ^ ^
#          |   | | +--- module patch (bug fixes)
#          |   | +----- module minor (features)
#          |   +------- module major (breaking changes)
#          +----------- Odoo version
```

## Why

- Without migration scripts, schema changes cause data loss or upgrade failures
- Pre-migration runs before ORM touches the schema — safe for destructive changes
- Post-migration uses the full ORM — convenient for data transformation
- Odoo only runs scripts for the specific version upgrade path

## References

- https://www.odoo.com/documentation/18.0/developer/howtos/upgrade_custom_db.html
- https://www.odoo.com/documentation/master/developer/reference/upgrades/upgrade_utils.html
