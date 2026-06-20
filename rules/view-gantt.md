---
priority: MAY
tags: [view, gantt]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create gantt view for planning/project"
    includes: ["views/*.xml"]
---
# Gantt View Configuration

## Description

Gantt views display records on a timeline bar chart, ideal for project planning and task scheduling. Gantt is available in Odoo 14+ but requires the `web_gantt` module (built-in from 15+).

## Correct

```xml
<record id="view_task_gantt" model="ir.ui.view">
    <field name="name">project.task.gantt</field>
    <field name="model">project.task</field>
    <field name="arch" type="xml">
        <gantt date_start="planned_date_begin"
               date_stop="planned_date_end"
               default_group_by="user_id"
               dependency="parent_id"
               dependency_type="ff"
               progress="progress"
               string="Tasks">
            <field name="name"/>
            <field name="user_id"/>
            <field name="progress"/>
        </gantt>
    </field>
</record>
```

## Key Attributes

| Attribute | Purpose |
|-----------|---------|
| `date_start` | Required — datetime for bar start |
| `date_stop` | Required — datetime for bar end |
| `default_group_by` | Row grouping field (user, project, etc.) |
| `dependency` | Many2one field for task dependency |
| `dependency_type` | `ff` (finish-to-finish) or `fs` (finish-to-start) |
| `progress` | Float field (0–100) for progress bar fill |
| `auto_schedule` | Enable auto-scheduling based on dependencies |
| `multi_edit` | Enable drag-to-reschedule |

## Incorrect

```xml
<gantt date_start="planned_date_begin">
    <field name="name"/>
    <!-- no date_stop — bars cannot render -->
</gantt>
```

## Rationale

- Both `date_start` and `date_stop` are required for rendering
- `dependency` + `dependency_type` enables automatic scheduling with arrow links
- `default_group_by` organizes rows (e.g., by assignee or project)
- `progress` shows visual completion fill inside each bar
- Declare all needed fields inside `<gantt>` for the tooltip/quick edit
- Gantt works in 14.0 via `web_gantt`; fully integrated from 15.0+

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
