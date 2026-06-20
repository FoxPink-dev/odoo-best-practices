---
priority: MAY
tags: [view, dashboard]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create dashboard view"
    includes: ["views/*.xml"]
---
# Dashboard View Practices

## Description

Dashboard views provide an overview of key metrics using a combination of graph, pivot, and kanban views in a single dashboard board. Odoo dashboards are typically implemented as custom views using the `board` view type or an embedded dashboard via `web_studio`. For 18.0+, use the dashboard view type or a kanban-based dashboard.

## Correct

```xml
<record id="view_crm_dashboard" model="ir.ui.view">
    <field name="name">crm.lead.dashboard</field>
    <field name="model">crm.lead</field>
    <field name="arch" type="xml">
        <dashboard>
            <view id="view_crm_lead_graph" type="graph"/>
            <view id="view_crm_lead_pivot" type="pivot"/>
            <view id="view_crm_lead_kanban" type="kanban"/>
        </dashboard>
    </field>
</record>

<record id="crm_dashboard_action" model="ir.actions.act_window">
    <field name="name">CRM Dashboard</field>
    <field name="res_model">crm.lead</field>
    <field name="view_mode">dashboard</field>
    <field name="view_id" ref="view_crm_dashboard"/>
</record>
```

## Dashboard via Board View (Odoo 15–19)

```xml
<record id="board_crm_dashboard" model="board.board">
    <field name="name">CRM Board</field>
    <field name="view_id" ref="view_crm_dashboard"/>
</record>
```

## Incorrect

```xml
<!-- Embedding raw JS in views — maintainability issue -->
<record id="view_custom_dashboard" model="ir.ui.view">
    <field name="arch" type="xml">
        <div>
            <script>// custom JS tracking</script>
        </div>
    </field>
</record>
```

## Rationale

- Dashboard views compose existing graph/pivot/kanban views — no duplication
- The `dashboard` type is the recommended approach for Odoo 16+
- Avoid inline JS; use OWL components if custom dashboard interactivity is needed
- Board views can be multi-column with multiple stacked sub-views
- Each sub-view can have its own domain context for filtered views

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
