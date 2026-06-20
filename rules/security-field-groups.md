---
priority: SHOULD
tags: [security, field-groups, field-level]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "restricting field visibility"
    includes: ["**/models/*.py"]
  - task: "adding sensitive fields"
    includes: ["**/models/*.py"]
---

# Security: Field-Level Groups Attribute

## Description

The `groups` attribute on model fields restricts which user groups can view and edit specific fields. This provides fine-grained access control at the field level beyond model-level ACLs and record rules.

## Correct

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Financial info - managers only
    credit_limit = fields.Monetary(
        string='Credit Limit',
        groups='account.group_account_manager',
    )

    # Sensitive personal data - HR group only
    emergency_contact = fields.Char(
        string='Emergency Contact',
        groups='hr.group_hr_user',
    )

    # Read-only for all except admin (field is visible but can't edit)
    contract_rate = fields.Float(
        string='Contract Rate',
        groups='base.group_system',
    )

    # Field visible to all but writable only via programmatic logic
    notes = fields.Text(string='Notes')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', **kwargs):
        """Make notes readonly for non-manager users at the view level."""
        res = super().fields_view_get(view_id=view_id, view_type=view_type, **kwargs)
        if not self.env.user.has_group('my_module.group_my_module_manager'):
            doc = etree.fromstring(res['arch'])
            for field in doc.xpath("//field[@name='notes']"):
                field.set('readonly', '1')
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
```

## Incorrect

```python
# WRONG: using incorrect group reference format
credit_limit = fields.Monetary(
    string='Credit Limit',
    groups='account.group_account_manager',  # Correct format: <module>.<xml_id>
)
# If the group is in module "my_module" with XML ID "group_account_manager",
# it should be "my_module.group_account_manager"

# WRONG: groups on fields that are used in search/domain
state = fields.Selection(
    selection=[('draft', 'Draft'), ('done', 'Done')],
    string='State',
    groups='my_module.group_my_module_manager',
)
# Search filters and domains referencing this field will fail for non-managers

# WRONG: field groups used without corresponding view adjustments
# The field is hidden for non-managers, but view attrs still reference it
```

## Rationale

- The `groups` attribute on a field restricts both read and write; users outside the specified group cannot see the field in any view.
- Use format `<module_name>.<xml_id>` for the group reference (e.g., `my_module.group_my_module_manager`).
- Field groups complement ACLs and record rules; they are the third security layer.
- **Important**: Fields used in search filters, domains, or computed field dependencies should NOT be group-restricted unless the dependent code also handles the restriction.
- For making a field visible but read-only to certain users, keep the field unrestricted and apply `readonly` in the view or via `fields_view_get()`.
- Field-level groups apply to all views — form, tree, search, kanban — users won't see the field anywhere.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
