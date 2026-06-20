---
priority: MUST
tags: [security, multi-company, company, data-isolation]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "implementing multi-company security"
    includes: ["**/models/*.py", "**/security/*.xml"]
  - task: "adding company_id field"
    includes: ["**/models/*.py"]
---

# Security: Multi-Company Patterns

## Description

Multi-company security ensures data isolation between companies in the same database. This involves proper `company_id` field setup, global record rules, and company-dependent behavior in business logic.

## Correct

```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
```

```xml
<!-- Global record rule for multi-company isolation -->
<record id="my_model_company_rule" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

```python
# Company-dependent field choices
class MyModel(models.Model):
    _name = 'my.model'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        domain="[('company_id', '=', company_id)]",
    )

    # Company-dependent computed fields
    local_price = fields.Float(
        string='Local Price',
        compute='_compute_local_price',
    )

    @api.depends('company_id')
    def _compute_local_price(self):
        for record in self:
            record.local_price = record.product_id.with_context(
                force_company=record.company_id.id
            ).lst_price
```

## Incorrect

```python
# WRONG: company_id not set when creating records
def action_create_from_wizard(self):
    self.env['my.model'].create({
        'name': 'Test',
        # Missing company_id - may use wrong company or fail
    })

# WRONG: company_id field missing on model
class MyModel(models.Model):
    _name = 'my.model'
    # No company_id - model is not company-aware
    # Multi-company rules cannot be applied

# WRONG: hardcoded company assumption
def get_company_records(self):
    return self.search([('company_id', '=', 1)])  # Should use self.env.company
```

## Rationale

- Every model that contains company-specific data must have a `company_id` field with `required=True` and `default=lambda self: self.env.company`.
- **Global record rule**: Always create a global record rule (no `groups` specified) with `domain_force=[('company_id', 'in', company_ids)]` to enforce data isolation across all users.
- `company_ids` in the domain is a special variable containing all companies the current user can access.
- Use `self.env.company` (not `self.env.user.company_id`) for the current company context.
- For computed fields that depend on company, use `force_company` in the context to ensure correct values.
- Multi-company rules are **global** rules, which means they _intersect_ with group rules. This ensures company isolation is never bypassed.
- Fields with `company_dependent=True` (stored in `ir.property`) handle per-company values automatically without defining `company_id`.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
- Odoo 17.0 Multi-company guidelines: https://www.odoo.com/documentation/17.0/developer/howtos/company.html
