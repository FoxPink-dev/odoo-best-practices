---
priority: MUST
tags: [migration, versioning, numbering]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "setting module version numbers"
    includes: ["__manifest__.py"]
  - task: "planning migration versions"
    includes: ["version", "migration"]
---
# Sequential Version Numbering

## Description

Module versions must follow a sequential, monotonically increasing scheme. Odoo uses the version from `__manifest__.py` to determine which migration scripts to run. Versions must be comparable as strings within the same series.

## Correct

```python
# Odoo 17 version scheme: <odoo_version>.<major>.<minor>.<patch>
"version": "17.0.1.0.0",   # Initial release
"version": "17.0.1.1.0",   # First migration
"version": "17.0.2.0.0",   # Major feature release
"version": "17.0.2.0.1",   # Patch release
```

```
migrations/
├── 17.0.1.1.0/
├── 17.0.2.0.0/
└── 17.0.2.0.1/
```

## Incorrect

```python
# WRONG: non-sequential version
"version": "17.0.1.5.0",   # Jump from 1.0.0 to 1.5.0 with no migration scripts
"version": "17.0.1.0.0",   # Going backward

# WRONG: inconsistent scheme
"version": "1.0",           # Missing Odoo version prefix
"version": "17.0.2024.1",   # Date-based version, not sequential
```

## Rationale

Odoo compares versions as strings to determine the migration path. It runs all migration directories whose version is greater than the currently installed version and less than or equal to the new version. Non-sequential jumps may skip migration directories. Always increment the patch/minor version for each set of migration scripts. Major version bumps (e.g., 1.x → 2.x) should be reserved for significant refactoring.

## References

- Odoo 17.0 Migration docs: Module version scheme
- migrate-version-bump — when to bump versions
- migrate-scripts-directory — migration directory naming
