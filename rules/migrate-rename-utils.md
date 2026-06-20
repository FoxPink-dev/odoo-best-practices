---
priority: SHOULD
tags: [migration, rename, column, table, orm]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "renaming fields during migration"
    includes: ["rename", "ALTER TABLE"]
  - task: "refactoring model names"
    includes: ["_name", "rename"]
---
# Safe Rename Utilities for Migration

## Description

When renaming fields, models, or tables during a migration, use helper utilities that preserve data integrity. Never drop a column before migrating its data. Use SQL ALTER statements carefully and always verify the column exists first.

## Correct

```python
def migrate(cr, version):
    # Safe rename: check column exists, copy data, drop old
    cr.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'sale_order' AND column_name = 'old_field'
    """)
    if cr.fetchone():
        cr.execute("ALTER TABLE sale_order RENAME COLUMN old_field TO new_field")
```

```python
# Using Odoo's column utilities (model rename)
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Safe model rename using ir.model.data
    if env.ref("my_module.old_xml_id", raise_if_not_found=False):
        env["ir.model.data"].search([
            ("model", "=", "old.model"),
            ("module", "=", "my_module"),
        ]).write({"model": "new.model"})
```

## Incorrect

```python
# WRONG: dropping old column before migrating data
def migrate(cr, version):
    cr.execute("ALTER TABLE sale_order DROP COLUMN old_field")
    cr.execute("ALTER TABLE sale_order ADD COLUMN new_field VARCHAR")
    cr.execute("UPDATE sale_order SET new_field = old_field")  # old_field is gone!
```

## Rationale

Column renames are safer than drop-and-recreate because they preserve all existing data, indexes, and constraints in one atomic operation. When a model is renamed, all XML references (`ref()`, `env.ref()`) and database entries in `ir_model`, `ir_model_fields`, and `ir_model_data` must be updated. Odoo's ORM does not automatically handle model renames — a migration script must update these system tables explicitly.

## References

- PostgreSQL ALTER TABLE documentation
- Odoo 17.0 Migration docs: Field and model rename patterns
- migrate-post-orm — using ORM for safe data migration
