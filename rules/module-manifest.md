---
priority: MUST
tags: [module, manifest, metadata]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating or editing __manifest__.py"
    includes: ["__manifest__.py"]
  - task: "reviewing module metadata"
    includes: ["__manifest__.py"]
---

# Module Manifest

## Description

The `__manifest__.py` file declares a Python package as an Odoo module and specifies its metadata. It must contain a single Python dictionary with required and optional keys.

## Correct

```python
{
    'name': 'Module Name',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Short one-line description of the module',
    'description': """
Long description of the module in reStructuredText format.
Can span multiple lines.
    """,
    'author': 'Author Name',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/menu_views.xml',
        'views/my_model_views.xml',
        'data/data.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/my_widget.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

## Incorrect

```python
{
    'name': 'module_name',  # Should use human-readable title case
    'version': '1.0',        # Missing Odoo version prefix
    'depends': ['base'],     # base is implicit, but should be explicit
    # Missing license, author, category
    'data': [
        'views/my_model_views.xml',  # Security CSV should come first
    ],
}
```

## Rationale

- `name` (required): Human-readable module name. Use title case, not snake_case.
- `version`: Follow semantic versioning with Odoo version prefix (e.g., `17.0.1.0.0`).
- `depends`: Must explicitly include all modules this module depends on, including `base`.
- `data`: File paths are relative to the module root. Security files must be listed before views.
- `license`: Defaults to `LGPL-3`. Must match the actual license of the module.
- `category`: Use existing categories from `ir_module_category_data.xml`. Hierarchy via `/` separator (e.g., `Foo / Bar`).
- `auto_install`: Use `True` only for glue/link modules that integrate two independently installed modules.
- `application`: Set to `True` only if this is a standalone app (appears in Apps dashboard).

## References

- Odoo 17.0 Module Manifests: https://www.odoo.com/documentation/17.0/developer/reference/backend/module.html
- Odoo Semver: https://semver.org
