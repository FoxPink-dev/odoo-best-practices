---
priority: MUST
tags: [migration, scripts, types, pre, post, end]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing migration scripts"
    includes: ["migrations/*/"]
  - task: "creating pre/post/end scripts"
    includes: ["pre-*", "post-*", "end-*"]
---
# Migration Script Types — pre, post, end

## Description

Odoo supports three types of migration scripts in `migrations/<version>/`: `pre-*.py` (before module updates), `post-*.py` (after module updates), and `end-*.py` (after all modules updated). Use the correct type for each operation.

## File Types

| Type | When It Runs | Use For |
|------|-------------|---------|
| `pre-*.py` | Before module data upgrades | Renaming columns, backing up data, schema changes |
| `post-*.py` | After module data upgrades | Migrating data to new columns, recomputing stored fields, updating XML IDs |
| `end-*.py` | After ALL modules upgraded | Cross-module data consistency, final cleanup |

## Correct

```
migrations/17.0.1.1.0/
├── pre-migrate_rename_column.py
├── post-migrate_populate_new_field.py
└── end-verify_consistency.py
```

```python
# pre-migrate_rename_column.py
def migrate(cr, version):
    cr.execute("ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS customer_ref VARCHAR")
    cr.execute("UPDATE sale_order SET customer_ref = partner_ref")
```

## Incorrect

```python
# WRONG: data migration in pre-script (module not yet upgraded)
def migrate(cr, version):
    # new_field doesn't exist yet — module not upgraded
    cr.execute("UPDATE sale_order SET new_field = old_field")
```

## Rationale

`pre-` scripts run before the module's XML/CSV data is loaded. If you need to access new fields or models, use `post-`. `end-` scripts run last across all modules, making them suitable for cross-module validation. Choosing the wrong type causes `column not found` or `relation does not exist` errors.

## References

- Odoo 17.0 Migration docs: Migration scripts
- migrate-scripts-directory — migration directory structure
