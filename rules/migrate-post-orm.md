---
priority: MUST
tags: [migration, post-orm, api, orm]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "using ORM in migration scripts"
    includes: ["post-*", "migration"]
  - task: "accessing models during migration"
    includes: ["self.env", "cr.execute"]
---
# Post-ORM Migration Scripts

## Description

Use `post-` scripts in `migrations/<version>/` when you need to access the ORM layer (models, fields, records). Post-scripts run after the module has been fully upgraded, so all new fields, models, and XML data are available.

## Correct

```python
# migrations/17.0.1.1.0/post-migrate_compute.py
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # ORM is fully available — new fields exist
    partners = env["res.partner"].search([("is_company", "=", True)])
    partners._compute_contact_count()
```

## Incorrect

```python
# WRONG: pre-script trying to use ORM features
# migrations/17.0.1.1.0/pre-migrate_compute.py
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # New fields may not exist yet — module not upgraded
    partners = env["res.partner"].search([("is_company", "=", True)])
    partners.write({"new_field": "value"})  # May fail
```

## Rationale

Post-scripts run after the module's data updates (XML, CSV) and model changes are applied. This means new columns exist, default data is loaded, and all ORM operations including computed fields, constraints, and onchange methods work correctly. Use `api.Environment(cr, SUPERUSER_ID, {})` to create an ORM environment inside a migration function. Always use post-scripts for data transformations that depend on new model fields.

## References

- Odoo 17.0 Migration docs: Post-migration scripts
- migrate-three-types — pre vs post vs end
- migrate-scripts-directory — directory structure
