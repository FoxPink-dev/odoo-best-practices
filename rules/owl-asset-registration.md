---
priority: SHOULD
tags: [owl, assets, bundle, manifest]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "registering JS assets"
    includes: ["__manifest__.py"]
  - task: "adding OWL components to bundles"
    includes: ["assets", "bundle"]
---
# OWL Asset Registration

## Description

OWL component assets (JS, XML, SCSS) must be registered in `__manifest__.py` under the appropriate asset bundle. Use the modern asset keys (`web.assets_backend`, `web.assets_frontend`) and include all three file types separately.

## Correct

```python
# __manifest__.py
{
    "name": "My Module",
    "version": "17.0.1.0.0",
    "assets": {
        "web.assets_backend": [
            "my_module/static/src/js/my_component.js",
            "my_module/static/src/xml/my_component.xml",
            "my_module/static/src/scss/my_component.scss",
        ],
    },
}
```

## Incorrect

```python
{
    "name": "My Module",
    "assets": {
        "web.assets_backend": [
            "my_module/static/src/my_module.js",       # WRONG: monolithic file
        ],
    },
}
```

## Rationale

Odoo 16+ uses the `assets` key in `__manifest__.py` (replacing the older `qweb` key for templates). Each asset type (JS/XML/SCSS) is registered independently. The asset system compiles and minifies them based on bundle dependencies. Missing asset declarations cause components to silently fail (templates not found, styles missing). Use `web.assets_backend` for backend views and `web.assets_frontend` for website/public pages.

## References

- Odoo 17.0 reference: Assets management
- Odoo 18.0 reference: Asset bundle configuration
- Odoo 19.0: Asset declaration format
