---
name: data-xml-id-naming
priority: MUST
tags:
  - data
  - xml-id
  - naming
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - create data file
  - define record
  - reference external id
---
# data-xml-id-naming — External ID Naming Conventions

External IDs (XML IDs) must follow a consistent naming pattern: `module.model_reference` or `module.type_subtype_reference`.

## Correct

```xml
<record id="model_my_model_demo_record" model="my.model">
  <field name="name">Demo Record</field>
</record>

<record id="product_product_demo_consulting" model="product.product">
  <field name="name">Consulting</field>
</record>

<record id="ir_sequence_sale_order" model="ir.sequence">
  <field name="code">sale.order</field>
</record>

<!-- Inherited view (module.model_inherit_views) -->
<record id="view_partner_form_inherit_sale" model="ir.ui.view">
  <field name="name">res.partner.sale.form.inherit</field>
</record>
```

## Incorrect

```xml
<!-- Ambiguous short id -->
<record id="record1" model="my.model">
  <field name="name">Demo</field>
</record>

<!-- No module prefix for cross-module reference -->
<record id="group_system" model="res.groups">
```

## Rationale

XML IDs are globally unique across all modules. A collision silently overwrites the first record. The convention `module_model_semantic_name` avoids collisions and makes the purpose clear at a glance. Cross-module references must use the full `<module>.<id>` notation.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/data.html#reference-ids
- https://www.odoo.com/documentation/18.0/contributing/development/coding_guidelines.html#xml-id-naming
