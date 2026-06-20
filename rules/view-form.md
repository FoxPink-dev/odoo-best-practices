---
priority: MUST
tags: [view, form]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify form view"
    includes: ["views/*.xml"]
---
# Form View Structure

## Description

Every form view must follow the canonical layout: `<header>` (action buttons), then `<sheet>` (main content with `<group>` and `<notebook>`), then optional `<div class="oe_chatter">`. The title appears as a `<h1>` inside `<sheet>` using `field` with `name` attribute.

## Correct

```xml
<form>
    <header>
        <button name="action_confirm" string="Confirm" type="object" class="btn-primary" states="draft"/>
        <button name="action_cancel" string="Cancel" type="object" states="draft,confirmed"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1><field name="name"/></h1>
            <group>
                <field name="partner_id"/>
                <field name="date_order"/>
            </group>
        </div>
        <notebook>
            <page string="Lines">
                <field name="order_line">
                    <tree editable="bottom">
                        <field name="product_id"/>
                        <field name="quantity"/>
                        <field name="price_unit"/>
                    </tree>
                </field>
            </page>
            <page string="Other Info">
                <group>
                    <field name="note"/>
                </group>
            </page>
        </notebook>
    </sheet>
    <div class="oe_chatter"/>
</form>
```

## Incorrect

```xml
<form>
    <!-- No header; buttons scattered; no statusbar -->
    <group>
        <field name="name"/>
        <field name="partner_id"/>
    </group>
    <button name="action_confirm" string="Confirm" type="object"/>
    <!-- flat layout without sheet/notebook pattern -->
</form>
```

## Rationale

- `<header>` with `statusbar_visible` drives the kanban/list state widget
- `<sheet>` provides a consistent card-like background and padding
- `<notebook>` organizes complex models into logical tabs
- `oe_chatter` shows the message thread and activity widgets
- Action buttons in header are always visible regardless of scroll
- `states` attribute on buttons automatically shows/hides based on record state

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_records.html
