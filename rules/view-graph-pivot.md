---
priority: SHOULD
tags: [view, graph, pivot]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify graph/pivot view"
    includes: ["views/*.xml"]
---
# Graph and Pivot View Design

## Description

Graph views provide visual aggregation with bar/line/pie charts. Pivot views provide tabular aggregation with row/column groups. Always define `<field>` with `type="row"`/`type="col"` (pivot) or `<field>` with `interval` (graph). Use `measure` attribute on `<graph>` to set default aggregation field.

## Correct

```xml
<record id="view_order_pivot" model="ir.ui.view">
    <field name="name">sale.order.pivot</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <pivot>
            <field name="date_order" type="row" interval="month"/>
            <field name="user_id" type="col"/>
            <field name="amount_total" type="measure"/>
        </pivot>
    </field>
</record>

<record id="view_order_graph" model="ir.ui.view">
    <field name="name">sale.order.graph</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <graph type="bar" stacked="1">
            <field name="date_order" interval="month"/>
            <field name="amount_total" type="measure"/>
            <field name="user_id"/>
        </graph>
    </field>
</record>
```

## Incorrect

```xml
<pivot>
    <field name="date_order"/>
    <field name="amount_total"/>
    <!-- no row/col/measure types specified -->
</pivot>

<graph>
    <field name="date_order"/>
    <field name="amount_total"/>
    <!-- no interval, no measure configuration -->
</graph>
```

## Rationale

- `type="row"`/`type="col"` in pivot defines the two axes of the table
- `interval="month"`/`week`/`day`/`year` controls date grouping granularity
- `type="measure"` marks the numeric field to aggregate (sum/avg/count)
- `stacked="1"` in graph stacks series by the grouping field
- `type="bar"`/`line`/`pie` selects the chart visualization style
- Pivot views auto-provide download to Excel and table-to-pivot toggle

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
