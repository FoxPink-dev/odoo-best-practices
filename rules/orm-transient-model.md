---
priority: MUST
tags: [orm, transient-model, wizard, abstract-model]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating wizard models"
    includes: ["models.TransientModel"]
  - task: "choosing model base class"
    includes: ["class.*models.", "models.Model", "models.AbstractModel", "models.TransientModel"]
  - task: "implementing wizards"
    includes: ["TransientModel"]
---
# ORM TransientModel vs AbstractModel vs Model

## Description

Use `models.Model` for regular database-persisted business objects. Use `models.TransientModel` for wizard data (temporary records stored in the database but regularly vacuumed). Use `models.AbstractModel` for mixins and abstract superclasses that should not have a database table. TransientModel records are automatically cleaned up based on `_transient_max_hours` (default 1.0) and `_transient_max_count` limits. All users can create TransientModel records, but can only access their own records (except superuser).

## Correct

```python
from odoo import models, fields

# Model for persistent business objects
class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sales Order'
    # Creates a database table 'sale_order'

# TransientModel for wizards
class SaleOrderConfirm(models.TransientModel):
    _name = 'sale.order.confirm'
    _description = 'Sales Order Confirmation Wizard'
    _transient_max_hours = 2.0
    _transient_max_count = 100

    order_id = fields.Many2one('sale.order', string="Order")
    confirmation_note = fields.Text(string="Note")

    def action_confirm(self):
        self.order_id.action_confirm()
        return {'type': 'ir.actions.act_window_close'}

# AbstractModel for mixins
class ApprovalMixin(models.AbstractModel):
    _name = 'approval.mixin'
    _description = 'Approval Mixin'

    approved_by = fields.Many2one('res.users', string="Approved By")
    approved_date = fields.Datetime(string="Approved On")

    def action_approve(self):
        self.write({
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
```

## Incorrect

```python
from odoo import models, fields

# WRONG: Using TransientModel for mixins (creates unnecessary DB table)
class ApprovalMixin(models.TransientModel):
    _name = 'approval.mixin'
    # TransientModel records are temporary and vacuumed — not suitable for mixins

# WRONG: Using Model for a wizard (clutters DB with permanent wizard data)
class SaleOrderConfirm(models.Model):
    _name = 'sale.order.confirm'
    # Wizard records persist forever and require manual cleanup
```

## Rationale

The Odoo 17.0 ORM docs define the three base classes: `Model` for "regular database-persisted models," `TransientModel` for "temporary data, stored in the database but automatically vacuumed every so often," and `AbstractModel` for "abstract super classes meant to be shared by multiple inheriting models." TransientModel has simplified access rights: "all users can create new records, and may only access the records they created. The superuser has unrestricted access." The automatic vacuum is controlled by `_transient_max_hours` (default 1.0 hour) and `_transient_max_count` (0 = unlimited).

## References

- Odoo 17.0 ORM docs: `AbstractModel` — alias of BaseModel, no database table
- Odoo 17.0 ORM docs: `Model` — main super-class for database-persisted models
- Odoo 17.0 ORM docs: `TransientModel` — temporarily persistent, regularly vacuum-cleaned
- Odoo 17.0 ORM docs: `_transient_max_hours` and `_transient_max_count` — vacuum controls
