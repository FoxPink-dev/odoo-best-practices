---
name: module-directory-layout
priority: critical
tags:
  - module
  - structure
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - new module
  - scaffold module
  - create addon
---

# module-directory-layout — Standard Module Structure

Odoo modules follow a convention-over-configuration directory layout. A consistent structure makes the module's purpose immediately clear to any developer.

## Incorrect

```
my_module/
├── __init__.py
├── __manifest__.py
├── my_file.py              # mixed models, wizard, reports
├── my_view.xml             # everything in one view file
└── security.xml            # security mixed with other data
```

## Correct

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── my_model.py
│   └── inherited_model.py
├── views/
│   ├── my_model_views.xml
│   ├── my_model_menus.xml
│   └── templates.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── my_model_data.xml
├── demo/
│   └── my_model_demo.xml
├── wizard/
│   └── my_wizard.py
├── report/
│   └── my_report.py
├── tests/
│   └── test_my_model.py
├── migrations/
│   └── 19.0.1.0.0/
│       ├── pre-migrate.py
│       └── post-migrate.py
└── static/
    └── src/
        ├── js/
        ├── xml/
        └── scss/
```

## Why

- **Discoverability**: Any Odoo developer knows where to find what
- **Maintainability**: Small files are easier to review and diff
- **OCA compliance**: Required for OCA contributions
- **Upgrade safety**: Clean separation makes version diffs clear

## References

- Official: https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html
- OCA: https://github.com/OCA/odoo-community.org
