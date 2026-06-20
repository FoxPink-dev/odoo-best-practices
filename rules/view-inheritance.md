---
priority: MUST
tags: [view, inheritance, xpath]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Extend or customize existing view"
    includes: ["views/*.xml"]
---
# View Inheritance (XPath) Best Practices

## Description

Always use `inherit_id` with explicit `xpath` expressions. Prefer position-based expressions (`expr` + `position`) over copying entire blocks. Use `//field[@name='...']` for field targeting or named elements. Never use `//group`/`//page` without additional qualifying attributes.

## Correct

```xml
<record id="view_partner_form_extension" model="ir.ui.view">
    <field name="name">res.partner.form.extension</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='email']" position="after">
            <field name="phone"/>
            <field name="mobile"/>
        </xpath>
        <xpath expr="//notebook/page[@string='Accounting']" position="before">
            <page string="Custom Tab">
                <group>
                    <field name="custom_field"/>
                </group>
            </page>
        </xpath>
        <xpath expr="//field[@name='state']" position="attributes">
            <attribute name="invisible">1</attribute>
        </xpath>
    </field>
</record>
```

## Incorrect

```xml
<record id="view_partner_form_extension" model="ir.ui.view">
    <field name="name">res.partner.form.extension</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//group" position="after">
            <!-- matches every <group> — too broad, breaks layout -->
            <field name="custom_field"/>
        </xpath>
    </field>
</record>
```

## Rationale

- `//field[@name='...']` is the most precise selector for adding adjacent fields
- Combining element type + `@name` + `@string` avoids unintended matches
- `position="attributes"` safely alters existing element properties
- `position="replace"` should be used sparingly; it breaks other inherits
- Always declare `model` matching the inherited view's model
- Test inheritance priority via `priority` field on the `ir.ui.view` record

## References

- https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html
