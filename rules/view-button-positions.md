---
priority: SHOULD
tags: [view, button, layout]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Add button to form view"
    includes: ["views/*.xml"]
---
# Button Placement: Header vs Sheet vs Inline

## Description

Buttons in Odoo form views have three distinct placement zones, each with a specific purpose. Correct placement follows Odoo UX conventions.

## Placement Rules

| Zone | Purpose | When to Use |
|------|---------|-------------|
| `<header>` | Primary actions | Confirm, Cancel, Validate, Send — workflow transitions |
| `<sheet>` (top) | Secondary actions | Print, More, Actions dropdown — non-workflow operations |
| `<sheet>` (inline) | Row-level actions | Add line, Remove, Edit — operations on sub-records |
| `<div class="oe_button_box">` | Status toggles | Archive, toggle features — visual binary state buttons |

## Correct

```xml
<form>
    <header>
        <button name="action_confirm" string="Confirm" type="object" class="btn-primary" states="draft"/>
        <button name="action_cancel" string="Cancel" type="object" states="draft,confirmed"/>
        <button name="action_send_email" string="Send by Email" type="object" class="btn-secondary"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <div class="oe_button_box">
            <button name="toggle_active" string="Archived" type="object" class="oe_stat_button"
                    icon="fa-archive" help="Set as archived"/>
        </div>
        <div class="oe_title">
            <h1><field name="name"/></h1>
        </div>
        <notebook>
            <page string="Lines">
                <field name="order_line">
                    <tree editable="bottom">
                        <button name="action_open_product" type="object" icon="fa-external-link"/>
                        <field name="product_id"/>
                        <field name="quantity"/>
                    </tree>
                </field>
            </page>
        </notebook>
    </sheet>
</form>
```

## Incorrect

```xml
<form>
    <sheet>
        <!-- Workflow action buttons inside sheet — reduces visibility -->
        <button name="action_confirm" string="Confirm" type="object"/>
        <button name="action_cancel" string="Cancel" type="object"/>
    </sheet>
    <header>
        <!-- Statusbar outside header — loses integration -->
        <field name="state" widget="statusbar"/>
    </header>
</form>
```

## Rationale

- Header buttons are always visible regardless of notebook tab or scroll position
- `oe_stat_button` gives a kanban-like stat card for counts or toggles
- Inline buttons in tree views should use `icon` for compact display
- `states` attribute auto-hides buttons based on record state
- Primary actions use `class="btn-primary"`, secondary use `btn-secondary`
- Avoid placing workflow buttons inside notebook pages

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_records.html
