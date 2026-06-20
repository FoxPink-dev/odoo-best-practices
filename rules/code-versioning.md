---
priority: MUST
tags: [coding-style, manifest, versioning]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing or updating __manifest__.py"
    includes: ["__manifest__.py", "__openerp__.py"]
---
# Code Versioning

## Description

Use semantic-like versioning in `__manifest__.py`: `<major>.<minor>.<patch>` (e.g., `17.0.1.0.0`). The first two digits match the Odoo major version. Bump versions on changes: increment patch for bug fixes, minor for new features, major for breaking changes. Always keep `version` in the manifest and include `license`, `author`, `category`, `summary`, and `depends`.

## Correct

```python
# __manifest__.py
{
    'name': 'My Custom Module',
    'version': '17.0.1.2.0',
    'license': 'LGPL-3',
    'author': 'My Company',
    'category': 'Sales',
    'summary': 'Extends sales with custom workflows',
    'depends': ['sale', 'sale_management'],
    'data': [
        'views/sale_order_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## Incorrect

```python
{
    'name': 'My Custom Module',
    'version': '1.0',  # Missing Odoo major version prefix
    # Missing license, category, summary
    'depends': ['sale'],
}
```

## Rationale

Odoo uses the version to determine upgrade order and detect changes. The `17.0.1.2.0` format means `17.0` = target Odoo version, `1` = major module version, `2` = minor, `0` = patch. Missing version info makes upgrades unreliable. The `license` field ensures compliance. The `depends` field must list all required modules; missing dependencies cause runtime errors.

## References

- Odoo 17.0 Module Manifest docs
- Odoo coding guidelines: `__manifest__.py` structure
