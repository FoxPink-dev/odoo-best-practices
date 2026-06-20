---
priority: MUST
tags: [module, dependencies, depends]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "adding depends to manifest"
    includes: ["__manifest__.py"]
  - task: "using features from other modules"
    includes: ["**/models/*.py"]
---

# Module Dependencies

## Description

The `depends` key in `__manifest__.py` declares which Odoo modules must be loaded before this one. Dependencies ensure correct module loading order and that required models, fields, and views exist.

## Correct

```python
# Minimal: always depend on base
'depends': ['base'],

# Standard: depend only on modules directly used
'depends': ['base', 'sale', 'stock'],

# Glue module: auto_install when both dependencies are present
'depends': ['sale', 'crm'],
'auto_install': True,

# External Python dependency
'external_dependencies': {
    'python': ['requests', 'openpyxl'],
    'bin': ['wkhtmltopdf'],
},
```

## Incorrect

```python
# WRONG: depending on too many modules just in case
'depends': ['base', 'sale', 'stock', 'account', 'crm', 'hr', 'project'],

# WRONG: missing explicit dependency on base
'depends': ['sale'],

# WRONG: unnecessary dependency (not using anything from purchase module)
'depends': ['base', 'sale', 'purchase'],

# WRONG: auto_install on a full application module
'depends': ['base', 'sale'],
'auto_install': True,  # Only for glue modules!
```

## Rationale

- Each dependency must be a module the code directly uses (inherits models, references fields, extends views).
- Avoid over-depending: every extra dependency increases installation time and coupling. Only include modules whose features you actually use.
- `base` must always be listed explicitly; this ensures the module updates when `base` updates.
- Use `external_dependencies` for Python packages or system binaries required by the module.
- Modules that are purely extensions of a single module should depend only on that module (e.g., `sale_extension` depends on `sale`, not on `stock` unless it directly uses stock features).
- For link/glue modules (e.g., `sale_crm`), use `auto_install: True` so they auto-install when both dependencies are present.

## References

- Odoo 17.0 Module Manifests: https://www.odoo.com/documentation/17.0/developer/reference/backend/module.html
