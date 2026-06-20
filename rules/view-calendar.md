---
priority: SHOULD
tags: [view, calendar]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify calendar view"
    includes: ["views/*.xml"]
---
# Calendar View Configuration

## Description

Calendar views display records on a date/time grid. Required attributes: `date_start`, `date_stop` (or `date_delay` for duration). Optional: `color`, `all_day`, `mode` (day/week/month), and `multi_edit`.

## Correct

```xml
<record id="view_calendar_event_calendar" model="ir.ui.view">
    <field name="name">calendar.event.calendar</field>
    <field name="model">calendar.event</field>
    <field name="arch" type="xml">
        <calendar date_start="start" date_stop="stop"
                  color="user_id" all_day="allday"
                  mode="month" multi_edit="1">
            <field name="name"/>
            <field name="user_id"/>
            <field name="location"/>
        </calendar>
    </field>
</record>
```

## Key Attributes

| Attribute | Purpose |
|-----------|---------|
| `date_start` | Required — datetime field for event start |
| `date_stop` | End datetime; alternative: `date_delay` |
| `date_delay` | Duration in float hours (alternative to `date_stop`) |
| `color` | Field to partition events by color |
| `all_day` | Boolean field for all-day events |
| `mode` | Default view: `day`, `week`, or `month` |
| `multi_edit` | Enable drag-and-drop reschedule |
| `quick_add` | Enable one-click event creation |

## Incorrect

```xml
<calendar date_start="start">
    <field name="name"/>
    <!-- no date_stop or date_delay — events have no duration -->
    <!-- no color — all events same color -->
</calendar>
```

## Rationale

- `date_start` is mandatory; without it the calendar will error
- `date_stop` or `date_delay` must be present for duration tracking
- `color` by user_id or stage_id provides visual partitioning
- `multi_edit` enables drag-and-drop date changes
- `all_day` prevents time-slot placement for full-day events
- Declare all fields used in tooltips/display inside `<calendar>` tags

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
