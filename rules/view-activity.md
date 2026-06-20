---
priority: SHOULD
tags: [view, activity]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify activity view"
    includes: ["views/*.xml"]
---
# Activity View Best Practices

## Description

Activity views display scheduled activities (calls, meetings, to-dos) related to a record. They are attached to models that inherit `mail.thread` (via `mail.thread` mixin). Activity views are configured by defining `activity_ids` in the form view's `oe_chatter` section or via a dedicated activity view.

## Activity View Type

```xml
<record id="view_crm_lead_activity" model="ir.ui.view">
    <field name="name">crm.lead.activity</field>
    <field name="model">crm.lead</field>
    <field name="arch" type="xml">
        <activity string="Activities">
            <field name="activity_ids"/>
            <templates>
                <div t-name="activity-box">
                    <div class="o_activity_body">
                        <strong><field name="activity_type_id"/></strong>
                        <div t-esc="record.summary.value"/>
                        <div class="o_activity_date">
                            <field name="date_deadline"/>
                        </div>
                    </div>
                </div>
            </templates>
        </activity>
    </field>
</record>
```

## Model Requirements

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

## Best Practices

- Always inherit `mail.activity.mixin` for activity support
- Configure activity types in data XML with `mail.activity.type`
- Use `activity_ids` in form views for inline activity display
- Set `date_deadline` and `activity_type_id` for schedule tracking
- Use `activity_user_id` for assignment-based routing

## Rationale

- Activity views drive Odoo's "Activities" sidebar and reminder system
- `mail.activity.mixin` provides `activity_ids`, `activity_state`, `activity_summary`
- Activity schedules integrate with calendar and notifications
- `activity_type_id` links to `mail.activity.type` for categorization (call, meeting, to-do)

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
