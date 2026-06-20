---
priority: MUST
tags: [module, migration, upgrade, post-migrate, pre-migrate]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing migration scripts"
    includes: ["**/migrations/**"]
  - task: "upgrading module versions"
    includes: ["__manifest__.py"]
---

# Module Upgrade and Migration Scripts

## Description

Migration scripts handle data transformations between module versions. They live in the `migrations/` directory and are executed automatically when a module is upgraded. Two types exist: `pre-migrate` (before data files load) and `post-migrate` (after data files load).

## Correct

```
my_module/
└── migrations/
    ├── 16.0.1.0.0/
    │   ├── pre-migrate.py
    │   └── post-migrate.py
    └── 17.0.1.0.0/
        ├── pre-migrate.py
        └── post-migrate.py
```

```python
# migrations/16.0.1.0.0/pre-migrate.py
# Runs BEFORE the module's data files are loaded

def migrate(cr, version):
    """Rename old field before new definition loads."""
    if not version:
        return  # Fresh install, skip migration
    cr.execute("""
        ALTER TABLE my_model
        RENAME COLUMN old_name TO name;
    """)
```

```python
# migrations/16.0.1.0.0/post-migrate.py
# Runs AFTER the module's data files are loaded

from odoo import fields, models


def migrate(cr, version):
    """Migrate data after new fields are installed."""
    env = api.Environment(cr, models.SuperuserContext(), {})
    # Transform data using ORM after schema changes
    records = env['my.model'].search([('state', '=', 'old_draft')])
    records.write({'state': 'draft'})
```

## Incorrect

```python
# WRONG: migration script with wrong directory naming
# Directory: my_module/migrations/16.0/
# Should be: my_module/migrations/16.0.1.0.0/

# WRONG: using ORM in pre-migrate (tables may not be ready)
def migrate(cr, version):
    env = api.Environment(cr, models.SuperuserContext(), {})
    records = env['my.model'].search([])  # May fail if schema not updated yet

# WRONG: no version check - runs on fresh install
def migrate(cr, version):
    # version is None on fresh install
    # This will crash
    cr.execute("UPDATE my_model SET name = 'migrated'")
```

## Rationale

- **Directory naming**: Migration directories must match the module version exactly (e.g., `17.0.1.0.0/`). The version is compared against the module's `version` in `__manifest__.py`.
- **`pre-migrate`**: Runs before the module's data files are loaded. Use for raw SQL operations like column renames, type changes, or data cleansing before new schemas apply.
- **`post-migrate`**: Runs after the module's data files are loaded. Use for ORM-based transformations since all fields, views, and data exist.
- **Version check**: Always check `if not version: return` at the top to skip migration on fresh installations (where `version` is `None`).
- **Idempotency**: Migration scripts must be idempotent. Running them multiple times should be safe.
- **Always use parameterized SQL**: Never use string formatting in raw SQL to avoid injection risks.

## References

- Odoo 17.0 Module Manifests: https://www.odoo.com/documentation/17.0/developer/reference/backend/module.html
- OpenUpgrade: https://github.com/OCA/OpenUpgrade
