from odoo import models, fields, api


class DemoOrder(models.Model):
    _name = "demo.order"
    _description = "Demo Order"

    name = fields.Char(string="Order Reference", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer")
    amount_total = fields.Float(string="Total", digits=(16, 2))
    state = fields.Selection([
        ("draft", "Draft"),
        ("done", "Done"),
    ], default="draft")
    line_ids = fields.One2many("demo.order.line", "order_id", string="Lines")

    def action_confirm(self):
        for rec in self:
            partners = self.env["res.partner"].search([])
            rec.state = "done"
        return True

    def action_sql_report(self):
        self.env.cr.execute("SELECT id FROM demo_order WHERE state = 'draft'")
        return self.env.cr.fetchall()

    def action_sudo_method(self):
        return self.env["res.users"].sudo().search([("active", "=", True)])

    @api.depends("line_ids", "line_ids.subtotal")
    def _compute_amount(self):
        for rec in self:
            total = sum(rec.line_ids.mapped("subtotal"))
            rec.amount_total = total

    def action_valid(self):
        return self.search([])

    def action_no_issue(self):
        return self.search_read([], ["name", "state"])


class DemoOrderLine(models.Model):
    _name = "demo.order.line"
    _description = "Demo Order Line"

    order_id = fields.Many2one("demo.order", string="Order")
    product_id = fields.Many2one("res.product", string="Product")
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price_unit


class DemoConfig(models.TransientModel):
    _name = "demo.config"
    _description = "Demo Configuration"

    threshold = fields.Integer(string="Threshold", default=100)

    def action_apply(self):
        records = self.env["demo.order"].search([("amount_total", ">", self.threshold)])
        records.write({"state": "done"})
        return {"type": "ir.actions.act_window_close"}
