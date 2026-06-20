---
priority: MUST
tags: [module, directory-structure, architecture]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating a new module"
    includes: ["__manifest__.py"]
  - task: "reviewing module structure"
    includes: ["**/models/**", "**/views/**", "**/security/**"]
---

# Module Directory Structure

## Description

Every Odoo module must follow a standardized directory layout. This ensures consistency, discoverability, and proper Python packaging across all modules.

## Correct

```
my_module/
├── __init__.py                 # Python package init
├── __manifest__.py             # Module metadata
├── models/                     # Business logic & data models
│   ├── __init__.py
│   └── my_model.py
├── views/                      # UI definitions (form, tree, search, kanban)
│   ├── my_model_views.xml
│   └── menu_views.xml
├── security/                   # Access control files
│   ├── ir.model.access.csv
│   └── security.xml            # Groups and record rules
├── data/                       # Default data (loaded always)
│   └── my_model_data.xml
├── demo/                       # Demo data (loaded only in demo mode)
│   └── demo_data.xml
├── controllers/                # HTTP endpoints
│   ├── __init__.py
│   └── main.py
├── static/                     # Static assets (CSS, JS, XML templates)
│   ├── description/
│   │   ├── icon.png            # 128x128 module icon
│   │   └── index.html
│   └── src/
│       ├── css/
│       ├── js/
│       └── xml/
├── wizard/                     # Transient/wizard models
│   ├── __init__.py
│   └── my_wizard.py
├── report/                     # QWeb report definitions
│   ├── __init__.py
│   ├── report.xml
│   └── report_template.xml
└── tests/                      # Unit tests
    ├── __init__.py
    └── test_my_model.py
```

## Incorrect

```
my_module/
├── my_module.py                # All logic in one file at root
├── __manifest__.py
├── my_module_view.xml          # Views at root level
├── security.csv                # Security mixed with other files
├── test_my_module.py           # Tests at root level
```

## Rationale

- Python requires `__init__.py` for package recognition; every subdirectory containing `.py` files must have one.
- Separating concerns into `models/`, `views/`, `security/`, `data/`, `demo/` allows the Odoo server to load files in the correct order and keeps the codebase navigable.
- The `static/description/icon.png` (128x128 PNG) is used in the Apps dashboard.
- The `wizard/` directory isolates transient models from persistent business models.
- Following the standard structure is a prerequisite for OCA (Odoo Community Association) module review.

## References

- Odoo 17.0 Module Manifests: https://www.odoo.com/documentation/17.0/developer/reference/backend/module.html
- Odoo 17.0 Your first module: https://www.odoo.com/documentation/17.0/administration/odoo_sh/getting_started/first_module.html
- OCA module structure: https://odoo-community.org/readme-structure
