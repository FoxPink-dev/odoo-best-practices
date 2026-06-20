---
priority: MUST
tags: [view, list, tree]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify tree/list view"
    includes: ["views/*.xml"]
---
# Tree/List View Best Practices

## Description

Use `<tree>` (14.0–18.0) or `<list>` (19.0+) for tabular views. Set `editable`, `default_order`, `multi_edit`, `import`, and `limit` declaratively. Always provide `default_order` for consistent UX. Prefer `editable="top"` for inline editing over opening the form view for simple models.

## Correct

```xml
<record id="view_order_list" model="ir.ui.view">
    <field name="name">sale.order.list</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <tree editable="top" default_order="date_order desc" multi_edit="1" import="1" limit="80">
            <field name="name"/>
            <field name="partner_id" optional="show"/>
            <field name="date_order"/>
            <field name="amount_total" sum="Total" widget="monetary"/>
            <field name="state" widget="badge" decoration-success="state == 'sale'" decoration-warning="state == 'draft'"/>
        </tree>
    </field>
</record>
```

## Incorrect

```xml
<record id="view_order_tree" model="ir.ui.view">
    <field name="name">sale.order.tree</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <tree>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date_order"/>
            <field name="amount_total"/>
            <!-- no default_order, no editable, no keyboard navigation -->
        </tree>
    </field>
</record>
```

## Rationale

- `default_order` prevents confusing sort states for users
- `editable` reduces clicks by allowing inline editing
- `multi_edit` enables batch operations on selected rows
- `optional="show"`/`optional="hide"` lets users customize columns
- `sum`/`avg` in footer gives instant aggregates
- `limit` controls pagination; Odoo default is 80
- `decoration-*` provides visual state cues

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
