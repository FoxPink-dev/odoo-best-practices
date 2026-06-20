---
priority: SHOULD
tags: [module, security, field-access, groups]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "adding fields with restricted access"
    includes: ["**/models/*.py"]
  - task: "reviewing field-level security"
    includes: ["**/models/*.py"]
---

# Module Field Access

## Description

Field-level access control restricts which user groups can read or write specific model fields. This is configured via the `groups` attribute on field definitions and complements ACLs and record rules.

## Correct

```python
from odoo import fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(string='Name', required=True)
    # Field visible to all users with access to the model

    # Sensitive field restricted to managers
    cost_price = fields.Float(
        string='Cost Price',
        groups='my_module.group_my_module_manager',
    )

    # Field visible to users, but only writable by managers
    notes = fields.Text(
        string='Notes',
        groups='base.group_user',
    )

    # Technical field restricted to admin/technical settings
    technical_config = fields.Json(
        string='Technical Config',
        groups='base.group_system',
    )

    def write(self, values):
        # Programmatic check for field-level gatekeeping
        if 'cost_price' in values and not self.env.user.has_group(
            'my_module.group_my_module_manager'
        ):
            raise AccessError(_("Only managers can change cost price."))
        return super().write(values)
```

## Incorrect

```python
# WRONG: using wrong module prefix in groups attribute
cost_price = fields.Float(
    string='Cost Price',
    groups='my_module.group_my_module_manager',  # Correct
)
# If the module is "my_module", the group XML ID is "my_module.group_my_module_manager"

# WRONG: overly broad field access for sensitive data
bank_account = fields.Char(string='Bank Account')
# No groups restriction → all model users can read/write

# WRONG: using groups on a stored compute field without recompute concerns
profit_margin = fields.Float(
    string='Profit Margin',
    compute='_compute_profit_margin',
    store=True,
    groups='my_module.group_my_module_manager',
)
```

## Rationale

- The `groups` attribute on fields restricts both visibility and editability. Users not in the specified group cannot see the field in views.
- Field groups use the format `<module>.<xml_id>` (e.g., `my_module.group_my_module_manager`).
- Use `groups` for sensitive data (financial info, personal data, technical settings).
- For fields that must be visible but not editable to some users, consider using view-level `attrs` or `readonly` with groups.
- Programmatic checks via `has_group()` are needed when field-level groups are bypassed through code (e.g., `write()` on `sudo()`).
- Views can override visibility: if a field appears in a view, the groups restriction still applies.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
