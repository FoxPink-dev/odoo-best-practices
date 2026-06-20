---
priority: MUST
tags: [orm, inheritance, _inherit, _inherits, model]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "extending a model"
    includes: ["_inherit", "_inherits"]
  - task: "creating model hierarchies"
    includes: ["class.*Model", "_inherit", "_name"]
---
# ORM Model Inheritance

## Description

Odoo provides three inheritance mechanisms: classic (`_inherit` with `_name` — creates a new model reusing another as base), extension (`_inherit` without `_name` — extends a model in-place), and delegation (`_inherits` — composition, exposes parent fields on child). Use extension (`_inherit` without `_name`) when adding fields or methods to existing models from other modules. Use classic inheritance when you need a new model that shares behavior with an existing one. Use delegation (`_inherits`) sparingly — it exposes parent fields but does not inherit methods, and chained `_inherits` is poorly supported.

## Correct

```python
from odoo import models, fields

# Extension: adding a field to an existing model (no _name)
class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_points = fields.Integer(string="Loyalty Points")

# Classic: new model inheriting from another
class Journey(models.Model):
    _name = 'travel.journey'
    _inherit = 'travel.booking'
    _description = 'Travel Journey'

    extra_insurance = fields.Boolean(string="Extra Insurance")

# Delegation: composition pattern
class Laptop(models.Model):
    _name = 'delegation.laptop'
    _description = 'Laptop'
    _inherits = {
        'delegation.screen': 'screen_id',
        'delegation.keyboard': 'keyboard_id',
    }

    name = fields.Char(string='Name')
    screen_id = fields.Many2one('delegation.screen', required=True, ondelete="cascade")
    keyboard_id = fields.Many2one('delegation.keyboard', required=True, ondelete="cascade")
```

## Incorrect

```python
from odoo import models, fields

# WRONG: fork instead of extend
class CustomResPartner(models.Model):
    _name = 'custom.res.partner'   # Creates separate table, not extending
    _inherit = 'res.partner'
    # This should be _inherit without _name to extend in-place

# WRONG: chained _inherits (unsupported)
class UltraLaptop(models.Model):
    _name = 'delegation.ultra.laptop'
    _inherits = {
        'delegation.laptop': 'laptop_id',
        'other.model': 'other_id',
    }
```

## Rationale

The Odoo 17.0 ORM documentation describes three mechanisms: classical inheritance (`_inherit` and `_name` together creates a new model), extension (`_inherit` without `_name` replaces/extends the existing model in-place), and delegation (`_inherits` dictionary mapping parent model names to Many2one field names). The docs warn: "`_inherits` is more or less implemented, avoid it if you can; chained `_inherits` is essentially not implemented, we cannot guarantee anything on the final behavior." Delegation only inherits fields, not methods. Extension is the standard way to customize existing models in a modular fashion.

## References

- Odoo 17.0 ORM docs: Inheritance and extension — three different mechanisms
- Odoo 17.0 ORM docs: Classical inheritance — `_inherit` + `_name`
- Odoo 17.0 ORM docs: Extension — `_inherit` without `_name`
- Odoo 17.0 ORM docs: Delegation — `_inherits` dictionary
- Odoo 17.0 ORM docs: Warning about `_inherits` implementation issues
