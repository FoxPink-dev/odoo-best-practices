---
name: data-noupdate
priority: MUST
tags:
  - data
  - noupdate
  - upgrade
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - define data record
  - create data file
  - module upgrade
---
# data-noupdate — `noupdate=1` vs `noupdate=0` Usage

Records with `noupdate="1"` are only created during module installation and skipped during upgrades. Records with `noupdate="0"` (default) are re-created on every upgrade, potentially overwriting user changes.

## Correct

```xml
<!-- noupdate="1": system data that users are expected to customize -->
<odoo noupdate="1">
  <record id="payment_term_30_days" model="account.payment.term">
    <field name="name">30 Days</field>
    <field name="line_ids" eval="[...]" />
  </record>

  <!-- Sequences (users must be able to edit) -->
  <record id="seq_sale_order" model="ir.sequence">
    <field name="name">Sale Order</field>
    <field name="code">sale.order</field>
  </record>
</odoo>

<!-- noupdate="0": structural data that must always match the code -->
<odoo>
  <record id="view_sale_order_form" model="ir.ui.view">
    <field name="name">sale.order.form</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
      <form />
    </field>
  </record>
</odoo>
```

## Incorrect

```xml
<!-- User-facing configuration locked from upgrades -->
<odoo noupdate="1">
  <record id="module_category_sales" model="ir.module.category">
    <field name="name">Sales</field>
  </record>
</odoo>
```

## Rationale

- `noupdate="1"` is for configuration data users are meant to modify: sequences, email templates, payment terms, fiscal positions, default accounts.
- `noupdate="0"` is for structural data: views, actions, menus, groups, categories — these must stay in sync with code.
- Putting structural data in `noupdate="1"` causes silent drift: upgrades won't apply fixes.
- Putting user-facing configuration in `noupdate="0"` resets customizations on every upgrade.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/data.html#noupdate
