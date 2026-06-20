---
name: data-demo-data
priority: MUST
tags:
  - data
  - demo
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - create demo data
  - add demo records
---
# data-demo-data — Demo Data Best Practices

Demo data must be placed in a separate `demo/` directory, declared only in the `demo` key of the manifest, and never mixed with production data.

## Correct

**Directory structure:**
```
my_module/
├── __manifest__.py      # demo: ['demo/my_model_demo.xml']
├── data/
│   └── my_model_data.xml
└── demo/
    └── my_model_demo.xml
```

**Manifest:**
```python
{
    'data': [
        'security/ir.model.access.csv',
        'data/my_model_data.xml',
        'views/my_model_views.xml',
    ],
    'demo': [
        'demo/my_model_demo.xml',
    ],
}
```

**Demo data file:**
```xml
<odoo>
  <record id="demo_product_1" model="product.product">
    <field name="name">Demo Product A</field>
    <field name="list_price">100.0</field>
  </record>
  <record id="demo_product_2" model="product.product">
    <field name="name">Demo Product B</field>
    <field name="list_price">250.0</field>
  </record>
</odoo>
```

## Incorrect

```python
# Mixing demo data with production data in manifest
{
    'data': [
        'data/my_model_data.xml',
        'demo/my_model_demo.xml',   # Wrong: demo in data key
    ],
}
```

## Rationale

- Demo data is not loaded in production databases unless `--without-demo=all` is explicitly set.
- Mixing demo files in the `data` key forces them on all installations.
- Demo data must never include sensitive or realistic information that could be mistaken for real data.
- Keep demo files small — they exist to demonstrate features, not to seed a database.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/module.html#demo-data
