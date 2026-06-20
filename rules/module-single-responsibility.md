---
name: module-single-responsibility
priority: critical
tags:
  - module
  - architecture
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - new module
  - organize module
  - split module
---

# module-single-responsibility — One Business Domain Per Module

Each module should address exactly one business domain. Mixing domains creates tight coupling, upgrade nightmares, and confusing dependencies.

## Incorrect

```python
# my_custom_addon/models.py — mixes HR, Accounting, and Sales
class Employee(models.Model):
    _name = 'hr.employee'
    # ...

class Invoice(models.Model):
    _name = 'account.move'
    # ...

class SaleOrder(models.Model):
    _name = 'sale.order'
    # ...
```

## Correct

```python
# hr_custom/models/employee.py
class Employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    # HR-specific logic only

# account_custom/models/invoice.py
class Invoice(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'
    # Accounting-specific logic only

# sale_custom/models/sale_order.py
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    # Sales-specific logic only
```

## Signs Your Module Is Doing Too Much

- `depends` list has 8+ unrelated modules
- Module name uses generic terms like `custom`, `utils`, `base`
- `models/` directory has files covering 3+ business domains
- `security/` defines groups for different domains
- Module can't be described in one sentence

## Benefits

- Modules can be enabled/disabled independently
- Upgrades are isolated — break one, not all
- Tests stay focused and fast
- Clear ownership per business domain

## References

- OCA guidelines: https://github.com/OCA/odoo-community.org
- Clean Architecture principles
