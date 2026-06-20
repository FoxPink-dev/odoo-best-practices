---
priority: MUST
tags: [security, sudo, privilege-escalation]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "using sudo() in business logic"
    includes: ["**/models/*.py"]
  - task: "reviewing privilege escalation"
    includes: ["**/*.py"]
---

# Security: When `sudo()` Is Appropriate vs Not

## Description

`sudo()` bypasses security rules (ACLs and record rules) to execute operations with superuser privileges. It must be used sparingly and only when necessary, with clear justification. Indiscriminate use of `sudo()` defeats Odoo's security model.

## Correct

```python
# OK: System operations that must work regardless of user permissions
def _create_analytic_entries(self):
    """Create analytic entries - always needed, not user-facing."""
    self.sudo()._create_entries()

# OK: Cross-user notification (user may not have access to recipient)
def _notify_participants(self):
    """Send notifications - bypass to ensure delivery."""
    for partner in self.partner_ids:
        self.sudo().message_post(
            partner_ids=[(4, partner.id)],
            body=_("You have been assigned."),
        )

# OK: Limited scope - only for specific field write
def action_confirm(self):
    """Confirm while updating a technical field the user can't normally write."""
    self.write({'state': 'confirmed'})  # Normal write
    self.sudo().write({'validated_by': self.env.user.id})  # Bypass for technical field

# OK: Cron method (always runs as admin)
def _cron_cleanup(self):
    """Cron method - runs as admin anyway."""
    records = self.search([('state', '=', 'expired')])
    records.unlink()
```

## Incorrect

```python
# WRONG: sudo() on every search - disables all security
def get_all_records(self):
    return self.sudo().search([])

# WRONG: sudo() to bypass record rules instead of fixing them
def get_other_users_records(self):
    user_id = self._context.get('bypass_user_id')
    # Rule exists to restrict by user_id, but sudo() bypasses it
    return self.sudo().search([('user_id', '=', user_id)])

# WRONG: sudo() in computed field (side effect + security bypass)
revenue = fields.Float(compute='_compute_revenue')
@api.depends('line_ids.price')
def _compute_revenue(self):
    for record in self:
        # sudo() inside compute is dangerous - may expose data incorrectly
        record.revenue = record.sudo().line_ids.mapped('price_total')

# WRONG: sudo().write() that silently overwrites protected data
def update_product_price(self):
    # Users without write access to product can still change prices via this method
    self.sudo().write({'list_price': 0.01})

# WRONG: passing sudo() records to other methods
def action_do_something(self):
    records = self.sudo().search([])
    records._do_something()  # Called methods will also run with sudo
```

## Rationale

- `sudo()` disables all ACLs and record rules for the operation. Use it only for operations that must work across all user contexts (crons, system notifications, technical field updates).
- Prefer well-designed record rules over `sudo()`. If users can't access certain records, fix the rules instead of bypassing them.
- Always minimize the `sudo()` scope: call it on the smallest possible recordset and for the shortest duration. Use `self.env.sudo()` for entire environment or `record.sudo()` for specific records.
- Log `sudo()` usage in sensitive operations for audit trails.
- Never expose `sudo()` through public methods that external users can trigger.
- In testing, avoid `sudo()` to test real security behavior.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
- Odoo ORM: https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html
