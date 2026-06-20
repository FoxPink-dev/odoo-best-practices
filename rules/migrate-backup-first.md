---
priority: CRITICAL
tags: [migration, backup, safety, disaster-recovery]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "running migration"
    includes: ["migration"]
  - task: "modifying data in migration"
    includes: ["cr.execute", "UPDATE", "DELETE", "ALTER"]
---
# Backup First — Always Backup Before Migration

## Description

Always create a full database backup before running any migration script. Migration scripts modify data irreversibly. Without a backup, a failed migration can cause permanent data loss or corruption.

## Correct

```bash
# Full database backup before migration
pg_dump -h localhost -U odoo -F c my_db > backup_$(date +%Y%m%d_%H%M%S).dump

# Then run migration
odoo -d my_db --stop-after-init -u my_module
```

```python
# pre-migrate_backup.py — warn if no backup marker exists
def migrate(cr, version):
    cr.execute("CREATE TABLE IF NOT EXISTS migration_backup_log (
        id SERIAL PRIMARY KEY,
        backed_up_at TIMESTAMP,
        script_name VARCHAR
    )")
```

## Incorrect

```python
# WRONG: destructive operation without backup
def migrate(cr, version):
    cr.execute("DELETE FROM sale_order_line WHERE state = 'draft'")
    # If this logic is wrong, data is permanently lost
```

## Rationale

Migration scripts execute within transactions, but once committed (end of script), changes are permanent. SQL errors, logic bugs, or unexpected data states can corrupt production data. A backup is the only reliable recovery mechanism. For production systems, test the migration on a staging copy first. Always verify the backup file is valid before starting the migration.

## References

- Odoo 17.0 Migration docs: Pre-migration checklist
- Odoo enterprise upgrade guide: Database backup procedures
