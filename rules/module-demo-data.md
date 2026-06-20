---
priority: SHOULD
tags: [module, demo-data, testing]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating demo data files"
    includes: ["**/demo/*.xml"]
  - task: "writing test data"
    includes: ["**/demo/*.xml"]
---

# Module Demo Data

## Description

Demo data provides realistic sample records to showcase module functionality. It is only loaded when Odoo starts in demo mode (with `--demo` or enabled in the database). Demo data must be clean, self-contained, and never interfere with production data.

## Correct

```xml
<!-- demo/demo_data.xml -->
<odoo>
    <record id="demo_product_1" model="my.model">
        <field name="name">Sample Product A</field>
        <field name="description">A sample product for demonstration</field>
        <field name="state">active</field>
        <field name="user_id" ref="base.user_demo"/>
    </record>

    <record id="demo_product_2" model="my.model">
        <field name="name">Sample Product B</field>
        <field name="description">Another sample product</field>
        <field name="state">draft</field>
        <field name="user_id" ref="base.user_demo"/>
    </record>
</odoo>
```

```python
# __manifest__.py
{
    # ...
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
}
```

## Incorrect

```xml
<!-- WRONG: demo XML IDs that conflict with real data -->
<record id="product_1" model="my.model">
    <field name="name">Default Product</field>
</record>
<!-- Missing "demo_" prefix may collide with production data XML IDs -->

<!-- WRONG: demo data mixed in with regular data files -->
<odoo>
    <record id="data_category" model="my.category">
        <field name="name">Real Category</field>
    </record>
    <record id="demo_product" model="my.model">
        <!-- This demo record will load in production -->
        <field name="name">Demo Product</field>
    </record>
</odoo>
```

## Rationale

- **Separate files**: Always put demo data in a dedicated `demo/` directory with files referenced in the `demo` key of the manifest. Never mix demo data with regular data files.
- **XML ID prefix**: Use `demo_` prefix for all demo data XML IDs to avoid conflicts with real data.
- **User references**: Assign demo data to `base.user_demo` (the demo user) rather than `base.user_root` or `base.user_admin`.
- **Realistic but safe**: Demo data should look realistic for evaluation purposes but be clearly identifiable as sample data (naming like "Sample Product").
- **Test independence**: Tests should not depend on demo data being present. Use `@tagged('-at_install', 'post_install')` or create test-specific data.
- **No side effects**: Demo data creation should not trigger side effects like sending emails, API calls, or expensive computations.

## References

- Odoo 17.0 Module Manifests: https://www.odoo.com/documentation/17.0/developer/reference/backend/module.html
