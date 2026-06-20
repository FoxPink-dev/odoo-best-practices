---
priority: SHOULD
tags: [api, report, pdf, qweb]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Create or modify PDF report"
    includes: ["reports/*.xml", "controllers/*.py"]
---
# QWeb PDF Report Best Practices

## Description

PDF reports use QWeb templates rendered by `ir.actions.report`. Define the report action in XML, the QWeb template in a separate file, and use the model's `_get_report_base_filename()` for the download filename.

## Report Action Definition

```xml
<record id="action_report_order" model="ir.actions.report">
    <field name="name">Sales Order Report</field>
    <field name="model">sale.order</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_sale_order</field>
    <field name="report_file">my_module.report_sale_order</field>
    <field name="binding_model_id" ref="sale.model_sale_order"/>
    <field name="binding_type">report</field>
    <field name="print_report_name">'SO-' + object.name</field>
</record>
```

## QWeb Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="report_sale_order">
        <t t-foreach="docs" t-as="o">
            <div class="page">
                <h2><span t-field="o.name"/></h2>
                <div class="row">
                    <div class="col-6">
                        <strong>Customer:</strong>
                        <p t-field="o.partner_id.name"/>
                        <p t-field="o.partner_id.email"/>
                    </div>
                    <div class="col-6">
                        <strong>Order Date:</strong>
                        <p t-field="o.date_order"/>
                    </div>
                </div>
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th class="text-right">Qty</th>
                            <th class="text-right">Price</th>
                            <th class="text-right">Subtotal</th>
                        </tr>
                    </thead>
                    <t t-foreach="o.order_line" t-as="line">
                        <tr>
                            <td><span t-field="line.product_id.name"/></td>
                            <td class="text-right"><span t-field="line.product_uom_qty"/></td>
                            <td class="text-right"><span t-field="line.price_unit"/></td>
                            <td class="text-right"><span t-field="line.price_subtotal"/></td>
                        </tr>
                    </t>
                </table>
                <p class="text-right">
                    <strong>Total: </strong><span t-field="o.amount_total"/>
                </p>
            </div>
        </t>
    </template>
</odoo>
```

## Incorrect

```xml
<template id="report_sale_order">
    <div class="page">
        <h2><span t-esc="docs.name"/></h2>
        <!-- t-esc without docs iteration — only first record rendered -->
    </div>
</template>
```

## Rationale

- Always use `t-foreach="docs"` — reports receive a recordset, not a single record
- `print_report_name` controls the download filename (Python expression)
- Use `report_type="qweb-pdf"` for PDF, `qweb-html` for in-browser preview
- `binding_model_id` attaches the report to the model's Print menu
- Use `t-field` (not `t-esc`) for proper Odoo field formatting (currencies, dates)
- External images in PDFs should use `data:uri` or file store attachments
- Style with Bootstrap classes — Odoo reports include Bootstrap CSS

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/reports.html
