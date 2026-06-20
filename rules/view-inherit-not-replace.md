---
name: view-inherit-not-replace
priority: medium-high
tags:
  - view
  - inheritance
  - customization
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - customize view
  - inherit view
  - modify form
---

# view-inherit-not-replace — Always Inherit Views

Never replace a base view. Always use `inherit_id` to extend existing views, or your customizations will conflict with other modules.

## Incorrect

```xml
<!-- Creates a new primary view — breaks other modules' inherits -->
<record id="view_partner_form_custom" model="ir.ui.view">
    <field name="name">res.partner.form.custom</field>
    <field name="model">res.partner</field>
    <field name="arch" type="xml">
        <form>
            <!-- complete redefinition — loses all other customizations -->
        </form>
    </field>
</record>
```

## Correct

```xml
<!-- Inherits and extends the existing view -->
<record id="view_partner_form_custom" model="ir.ui.view">
    <field name="name">res.partner.form.custom</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='email']" position="after">
            <field name="phone"/>
            <field name="mobile"/>
        </xpath>
    </field>
</record>
```

## View Inheritance Position Options

| Position | Behavior |
|----------|----------|
| `after` | Insert after the matched element |
| `before` | Insert before the matched element |
| `inside` | Insert as first child of matched element |
| `replace` | Replace the matched element entirely |
| `attributes` | Modify attributes of matched element |

## Why

- Multiple modules can coexist without conflicts
- View inheritance is layered in priority order
- Replacing breaks the inheritance chain for all other modules
- Odoo's view resolution merges all inherits into one final arch

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
