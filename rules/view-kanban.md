---
priority: SHOULD
tags: [view, kanban]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify kanban view"
    includes: ["views/*.xml"]
---
# Kanban View Best Practices

## Description

Kanban views display records as cards. Structure: `<kanban>` with `default_group_by` and `class`, then `<templates>` with `<t t-name="kanban-box">`. Use `<field>` for displayed data, `<t t-esc="">` for computed values, and QWeb conditional attributes for visual state.

## Correct

```xml
<record id="view_crm_lead_kanban" model="ir.ui.view">
    <field name="name">crm.lead.kanban</field>
    <field name="model">crm.lead</field>
    <field name="arch" type="xml">
        <kanban default_group_by="stage_id" class="o_kanban_mobile">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="email_from"/>
            <field name="expected_revenue"/>
            <field name="stage_id"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_global_click">
                        <div class="o_kanban_image">
                            <img t-att-src="kanban_image('crm.lead', 'image_128', record.id.value)" alt="Avatar"/>
                        </div>
                        <div class="oe_kanban_details">
                            <strong><field name="name"/></strong>
                            <div><field name="partner_id"/></div>
                            <div><field name="expected_revenue" widget="monetary"/></div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

## Incorrect

```xml
<kanban>
    <templates>
        <t t-name="kanban-box">
            <div>
                <field name="name"/>
                <field name="expected_revenue"/>
            </div>
        </t>
    </templates>
</kanban>
```

## Rationale

- `default_group_by` uses column/kanban stage grouping on open
- `<field>` declarations make fields available to Qwen templates
- `kanban_image()` helper loads images lazily without blocking
- `oe_kanban_global_click` makes the whole card clickable
- `oe_kanban_details` provides consistent card padding
- `o_kanban_mobile` class enables mobile-responsive card layout

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
