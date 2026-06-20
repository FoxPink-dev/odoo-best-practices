---
name: data-default-data
priority: MUST
tags:
  - data
  - default
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - ship default data
  - create base configuration
---
# data-default-data — Default Data That Ships With Modules

Default (non-demo) data provides essential configuration records that every installation of a module needs. These go in `data/` and are declared in the `data` manifest key. Only include data that is truly required for the module to function.

## Correct

```xml
<odoo>
  <!-- Minimal chart of accounts template -->
  <record id="account_template_standard" model="account.chart.template">
    <field name="name">Standard Chart of Accounts</field>
    <field name="currency_id" ref="base.EUR"/>
  </record>

  <!-- Default sales team -->
  <record id="team_sales_department" model="crm.team">
    <field name="name">Sales</field>
    <field name="sequence">10</field>
  </record>

  <!-- Default stage for leads -->
  <record id="stage_lead1" model="crm.stage">
    <field name="name">New</field>
    <field name="sequence">10</field>
    <field name="is_won">False</field>
  </record>
</odoo>
```

## Incorrect

```xml
<!-- Too much default data: records users will almost certainly delete -->
<odoo>
  <record id="res_partner_title_1" model="res.partner.title">
    <field name="name">Dr.</field>
  </record>
  <record id="res_partner_title_2" model="res.partner.title">
    <field name="name">Prof.</field>
  </record>
</odoo>
```

## Rationale

- Every record in `data/` is created on every database where the module is installed — including production.
- Only ship data that is genuinely required: stages, sequences, default configuration, base categories.
- Data that is only useful for showcasing features belongs in `demo/`.
- Overloading default data creates unnecessary clutter and migration burden. When in doubt, leave it out.
- All default data should be wrapped in `<odoo noupdate="1">` when users are expected to modify it.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/module.html#data
