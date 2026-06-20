---
priority: MUST
tags: [migration, version, manifest, bump]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "updating module version"
    includes: ["__manifest__.py"]
  - task: "bumping version for migration"
    includes: ["version", "migration"]
---
# Migration Version Bump

## Description

Always increment the module version in `__manifest__.py` when adding migration scripts. The version must follow a consistent scheme and the migration directory name must match the new version exactly.

## Correct

```python
# __manifest__.py — before migration
"version": "17.0.1.0.0",

# After adding migration scripts
"version": "17.0.1.1.0",
```

```
migrations/17.0.1.1.0/
└── post-migrate_data.py
```

## Incorrect

```python
# Wrong: version not bumped, but migration scripts exist
"version": "17.0.1.0.0",
```

```
migrations/17.0.1.0.0/     # Wrong: directory named after old version
└── post-migrate_data.py
```

## Rationale

Odoo detects migration scripts by comparing the installed version (from `ir_module_module`) with the manifest version. If the versions match, no migration runs. If the manifest version is higher, Odoo runs all migration scripts in directories between the old and new version. Without a version bump, migration scripts are silently skipped.

## References

- Odoo 17.0 Migration docs: Version bumping
- migrate-sequential-versions — version numbering scheme
