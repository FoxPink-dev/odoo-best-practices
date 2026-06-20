---
name: view-new-list-tag
priority: medium-high
tags:
  - view
  - list
  - migration
odoo_versions:
  - 19
triggers:
  - create list view
  - migrate to 19
---

# view-new-list-tag — Use `<list>` Instead of `<tree>` in Odoo 19+

Odoo 19 renamed the `<tree>` tag to `<list>`. Both work for backward compatibility, but new code should use `<list>`.

## Incorrect

```xml
<record id="view_order_tree" model="ir.ui.view">
    <field name="name">sale.order.tree</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <tree>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="amount_total" sum="Total"/>
        </tree>
    </field>
</record>
```

## Correct

```xml
<record id="view_order_list" model="ir.ui.view">
    <field name="name">sale.order.list</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <list>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="amount_total" sum="Total"/>
        </list>
    </field>
</record>
```

## Key `<list>` Attributes

| Attribute | Purpose |
|-----------|---------|
| `editable="top"` / `editable="bottom"` | Inline editing |
| `multi_edit="1"` | Enable batch edit |
| `default_group_by="field"` | Default grouping |
| `limit="80"` | Records per page |
| `import="1"` | Enable CSV import |

## Field Attributes in List Views

| Attribute | Purpose |
|-----------|---------|
| `sum="Total"` | Footer sum |
| `avg="Avg"` | Footer average |
| `widget="progressbar"` | Progress bar |
| `colors` | Conditional coloring |

## Why

- `<list>` is canonical in Odoo 19+, `<tree>` is legacy alias
- Future versions may deprecate `<tree>` entirely
- Consistency across the codebase avoids confusion

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
