---
priority: MEDIUM
tags: [migration, openupgrade, odoo-version, major-upgrade]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "upgrading Odoo major version"
    includes: ["openupgrade", "major upgrade"]
  - task: "cross-version migration"
    includes: ["migration", "14", "15", "16", "17", "18"]
---
# OpenUpgrade Compatibility

## Description

When performing major Odoo version upgrades (e.g., 16.0 → 17.0), use OpenUpgrade scripts for database migration. OpenUpgrade handles column renames, model changes, and data transformations that occur between Odoo versions.

## Correct

```bash
# Use OpenUpgrade scripts from the community repository
git clone https://github.com/OCA/OpenUpgrade.git
cd OpenUpgrade

# Run migration with OpenUpgrade
python odoo-bin -d my_db --upgrade --openupgrade \
    --load=base,web,openupgrade_framework \
    --stop-after-init
```

```python
# Module-specific OpenUpgrade migration script
# migrations/17.0.1.0.0/pre-migrate_openupgrade.py
def migrate(cr, version):
    """Handle field rename introduced in Odoo 17."""
    openupgrade.rename_columns(cr, {
        "sale_order": [("old_field", "new_field")],
    })
```

## Incorrect

```python
# WRONG: attempting major version upgrade without OpenUpgrade
# Just running -u all on the new codebase
# This will fail if any column was renamed by Odoo core
```

## Rationale

Odoo's standard `-u` mechanism upgrades module data but does not handle structural database changes between major versions (e.g., column renames in core models, table merges, or data format changes). OpenUpgrade provides a community-maintained mapping of all changes between Odoo versions. Without it, major version upgrades will fail with "column not found" errors or produce corrupt data. Always run a trial migration on a staging database first.

## References

- OCA OpenUpgrade repository: https://github.com/OCA/OpenUpgrade
- Odoo 17.0 Migration docs: Major version upgrade guide
- Odoo 18.0 → 19.0 migration notes: breaking changes
