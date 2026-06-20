---
name: data-email-templates
priority: SHOULD
tags:
  - data
  - email
  - template
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - create email template
  - define mail template
---
# data-email-templates — Email Template Data XML Patterns

Email templates use `mail.template` and support QWeb rendering, inline variables, and multi-language translations. They must use `noupdate="1"` so users can customize them.

## Correct

```xml
<odoo noupdate="1">
  <record id="email_template_sale_order" model="mail.template">
    <field name="name">Sale Order: Confirmation</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="email_from">${object.company_id.email}</field>
    <field name="subject">Order ${object.name} confirmed</field>
    <field name="partner_to">${object.partner_id.id}</field>
    <field name="auto_delete" eval="True"/>
    <field name="body_html" type="html">
      <div style="font-family: Arial, sans-serif;">
        <p>Dear ${object.partner_id.name},</p>
        <p>Your order <strong>${object.name}</strong> has been confirmed.</p>
        <p>Total: ${object.amount_total}</p>
      </div>
    </field>
  </record>
</odoo>
```

## Incorrect

```xml
<!-- Missing noupdate: user customizations will be lost on upgrade -->
<odoo>
  <record id="email_template_sale_order" model="mail.template">
    <field name="name">Sale Order: Confirmation</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="subject">Order confirmed</field>
    <field name="body_html" type="html"><![CDATA[...]]></field>
  </record>
</odoo>
```

## Rationale

- Email templates are user-facing content — always put them in `noupdate="1"`.
- Use `${object.field}` syntax for placeholder variables; avoid hardcoding values.
- Prefer `partner_to` (Odoo resolves the recipient) over `email_to` (raw email string).
- Use `model_id` to bind the template to a specific model, enabling automatic rendering context.
- Set `auto_delete="True"` for transactional emails (notifications) to avoid mailbox bloat.
- Keep HTML clean and responsive; use inline styles as email clients strip `<style>` tags.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/data.html#email-templates
- https://www.odoo.com/documentation/18.0/applications/general/companies/email_template.html
