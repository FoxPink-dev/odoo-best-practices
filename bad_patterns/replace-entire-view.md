---
name: replace-entire-view
severity: high
tags:
  - anti-pattern
  - view
  - inheritance
---

# Replacing Entire View Instead of Inheriting

## ❌ Anti-Pattern

```xml
<record id="view_partner_form_custom" model="ir.ui.view">
    <field name="name">res.partner.form.custom</field>
    <field name="model">res.partner</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <!-- Completely redefined form -->
                <!-- Other modules' inherits are LOST -->
            </sheet>
        </form>
    </field>
</record>
```

## ✅ Fix

```xml
<record id="view_partner_form_custom" model="ir.ui.view">
    <field name="name">res.partner.form.custom</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='email']" position="after">
            <field name="phone"/>
        </xpath>
    </field>
</record>
```

## Why It Hurts

Creating a new primary view breaks all other modules' view inherits. Odoo's view resolution picks the **lowest priority** primary view. Your replacement may silently win, and every other customization disappears.

## Detected When

- `inherit_id` is missing from view record
- View has complete form/list/kanban redefinition instead of targeted xpath or position-based changes
- Module claims to "override" a view instead of "extend" it

## References

- view-inherit-not-replace
