---
priority: SHOULD
tags: [view, search]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify search view"
    includes: ["views/*.xml"]
---
# Search View Design

## Description

Search views control filters, groupings, and default sort in list/kanban views. Use `<field>` for searchable fields, `<filter>` for predefined filters, `<separator>` for grouping filters, and `<group expand="0">` for collapsible sections. Always name filters with `name` for extensibility.

## Correct

```xml
<record id="view_order_search" model="ir.ui.view">
    <field name="name">sale.order.search</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <search>
            <field name="name" filter_domain="[('name','ilike',self)]" string="Order Reference"/>
            <field name="partner_id"/>
            <field name="user_id"/>
            <filter name="filter_my_orders" string="My Orders" domain="[('user_id','=',uid)]"/>
            <filter name="filter_draft" string="Draft" domain="[('state','=','draft')]"/>
            <separator/>
            <filter name="group_by_partner" string="Partner" context="{'group_by':'partner_id'}"/>
            <filter name="group_by_date" string="Order Date" context="{'group_by':'date_order:month'}"/>
            <group expand="0" string="Advanced">
                <filter name="filter_confirmed" string="Confirmed" domain="[('state','=','confirmed')]"/>
                <filter name="filter_done" string="Done" domain="[('state','=','done')]"/>
            </group>
        </search>
    </field>
</record>
```

## Incorrect

```xml
<search>
    <field name="name"/>
    <filter domain="[('state','=','draft')]" string="Draft"/>
    <!-- no named filters, no separators, no grouping -->
</search>
```

## Rationale

- Named filters enable other modules to extend/search via inherit_id
- `<separator>` creates mutually exclusive filter groups (AND vs OR logic)
- `<group expand="0">` keeps advanced filters hidden by default
- `filter_domain` on fields provides custom search logic beyond simple equality
- `group_by` with `:month`/`:year` suffix enables date grouping at different granularities
- `uid` in domain refers to current user for personal filters

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
