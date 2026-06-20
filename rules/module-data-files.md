---
priority: MUST
tags: [module, data-files, noupdate, xml]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating data XML files"
    includes: ["**/data/*.xml"]
  - task: "editing __manifest__.py data list"
    includes: ["__manifest__.py"]
---

# Module Data Files

## Description

Data files in Odoo define records that are loaded during module installation and updates. Proper ordering, `noupdate` usage, and separation of demo vs. regular data are critical for maintainability.

## Correct

```python
# __manifest__.py: correct ordering
'data': [
    # 1. Security (must be first)
    'security/ir.model.access.csv',
    'security/security.xml',
    # 2. Sequences
    'data/ir_sequence_data.xml',
    # 3. Data (default data, categories, etc.)
    'data/data.xml',
    # 4. Actions & menus
    'views/menu_views.xml',
    # 5. Views (form, tree, search, kanban)
    'views/my_model_views.xml',
    # 6. Wizards
    'wizard/my_wizard_views.xml',
    # 7. Reports
    'report/report.xml',
    # 8. Templates (QWeb)
    'views/templates.xml',
],
'demo': [
    'demo/demo_data.xml',
],
```

```xml
<!-- noupdate="1": system data that should NOT be overwritten on upgrades -->
<odoo noupdate="1">
    <record id="seq_my_model" model="ir.sequence">
        <field name="name">My Model Sequence</field>
        <field name="code">my.model</field>
        <field name="padding">5</field>
    </record>
</odoo>

<!-- noupdate="0": data that should be re-applied on every upgrade -->
<odoo noupdate="0">
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
    </record>
</odoo>
```

## Incorrect

```xml
<!-- WRONG: security listed after views -->
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
</record>

<!-- WRONG: data that users edit should be noupdate="1" -->
<odoo noupdate="0">
    <record id="email_template_my_model" model="mail.template">
        <field name="name">My Model Email</field>
    </record>
</odoo>
```

## Rationale

- **Security files first**: ACLs and record rules must be loaded before any data records or views to prevent access errors during installation.
- **`noupdate="1"`**: Use for records that users may customize after installation (sequences, email templates, scheduled actions, default data). They are created on install but not overwritten on module upgrades.
- **`noupdate="0"`** (default): Use for views, menus, actions, and other structural records that must be refreshed on every upgrade.
- **Avoid `noupdate="1"` on views/menus**: This prevents upgrades from applying improvements to these structures.
- **Demo data**: Always separate into `demo/` directory and reference only in the `demo` key of the manifest. Demo data is only loaded in demo mode.
- **Resource paths**: Always relative to the module root, using forward slashes.

## References

- Odoo 17.0 Data Files: https://www.odoo.com/documentation/17.0/developer/reference/backend/data.html
- Odoo 17.0 Module Manifests: https://www.odoo.com/documentation/17.0/developer/reference/backend/module.html
