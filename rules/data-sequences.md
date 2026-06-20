---
name: data-sequences
priority: SHOULD
tags:
  - data
  - sequence
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - define sequence
  - create document numbering
---
# data-sequences — Sequence Data XML Patterns

Sequences provide automatic numbering for documents. They must use `ir.sequence` with proper prefixes, padding, and `noupdate="1"` to allow customization.

## Correct

```xml
<odoo noupdate="1">
  <record id="seq_sale_order" model="ir.sequence">
    <field name="name">Sale Order</field>
    <field name="code">sale.order</field>
    <field name="prefix">SO</field>
    <field name="padding">5</field>
    <field name="company_id" eval="False"/>
    <field name="implementation">standard</field>
  </record>

  <record id="seq_purchase_order" model="ir.sequence">
    <field name="name">Purchase Order</field>
    <field name="code">purchase.order</field>
    <field name="prefix">PO/%(year)s/</field>
    <field name="padding">5</field>
    <field name="company_id" eval="False"/>
    <field name="implementation">standard</field>
  </record>
</odoo>
```

## Incorrect

```xml
<!-- Missing noupdate: will reset sequence counter on every upgrade -->
<odoo>
  <record id="seq_sale_order" model="ir.sequence">
    <field name="name">Sale Order</field>
    <field name="code">sale.order</field>
    <field name="prefix">SO</field>
    <field name="padding">5</field>
  </record>
</odoo>
```

## Rationale

- Sequences **must** be `noupdate="1"` so administrators can change the prefix/padding and so the next-number counter is not reset on upgrade.
- Use `implementation="standard"` (no gap) or `implementation="no_gap"` based on legal requirements.
- Date-based prefixes like `SO/%(year)s/%(month)s/` aid document filtering.
- Set `company_id="False"` for a company-independent sequence, or scope it properly for multi-company.
- Always test sequences with a dry-run install to verify the prefix renders correctly.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/data.html#sequences
