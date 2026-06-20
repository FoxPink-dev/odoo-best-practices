---
priority: SHOULD
tags: [api, email, template, mail]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify email template"
    includes: ["data/*.xml", "views/*.xml"]
---
# Email Template Design

## Description

Email templates use `mail.template` model with QWeb rendering for dynamic content. Define templates in XML data files with `model_id`, `subject`, `email_from`, `email_to`, and `body_html`. Use `t-field` for safe field rendering and `t-esc` for raw values.

## Correct

```xml
<record id="email_template_order" model="mail.template">
    <field name="name">Sales Order Email</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="subject">{{ object.name }} — Confirmed</field>
    <field name="email_from">{{ object.company_id.email or '' }}</field>
    <field name="email_to">{{ object.partner_id.email or '' }}</field>
    <field name="reply_to">{{ object.user_id.email or '' }}</field>
    <field name="partner_to">{{ object.partner_id.id }}</field>
    <field name="auto_delete" eval="True"/>
    <field name="body_html" type="html">
        <div style="font-family: Arial, sans-serif;">
            <h2>Dear <span t-field="object.partner_id.name"/>,</h2>
            <p>Your order <strong><span t-field="object.name"/></strong> has been confirmed.</p>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f0f0f0;">
                        <th style="padding: 8px;">Product</th>
                        <th style="padding: 8px; text-align: right;">Qty</th>
                        <th style="padding: 8px; text-align: right;">Price</th>
                    </tr>
                </thead>
                <tbody>
                    <t t-foreach="object.order_line" t-as="line">
                        <tr>
                            <td style="padding: 8px;"><span t-field="line.product_id.name"/></td>
                            <td style="padding: 8px; text-align: right;"><span t-field="line.product_uom_qty"/></td>
                            <td style="padding: 8px; text-align: right;"><span t-field="line.price_unit"/></td>
                        </tr>
                    </t>
                </tbody>
            </table>
            <p style="margin-top: 20px;">
                <strong>Total: <span t-field="object.amount_total"/></strong>
            </p>
            <p>Best regards,<br/><span t-field="object.company_id.name"/></p>
        </div>
    </field>
</record>
```

## Incorrect

```xml
<record id="email_template_order" model="mail.template">
    <field name="name">Sales Order Email</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="subject">Order Confirmed</field>
    <field name="body_html" type="html">
        <p>Your order has been confirmed.</p>
        <!-- static content — no dynamic fields, no partner context -->
    </field>
    <!-- no email_to, no partner_to — cannot be sent -->
</record>
```

## Rationale

- `partner_to` links the email to the partner's communication history (chatter)
- `email_from` and `reply_to` should come from the company or salesperson
- `auto_delete` prevents template clutter after use (for transactional emails)
- Inline CSS is recommended for email clients that strip `<style>` blocks
- Use `object` (record) and `ctx` (context) in template expressions
- Always provide `model_id` so the template knows which model to render
- Test with `mail.render_template()` to verify QWeb syntax before sending

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/mail.html
