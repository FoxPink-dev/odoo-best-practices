---
name: knowledge-res-users
model: res.users
module: base
priority: high
---
# res.users — Users & Access Rights

## Purpose
Represents system users with authentication, access rights, groups, and preferences. Extends `res.partner`.

## Key Fields
- `partner_id` — Many2one to `res.partner` (name, email, address)
- `company_id` — Many2one to `res.company` (main company)
- `company_ids` — Many2many accessible companies
- `groups_id` — Many2many to `res.groups` (security groups)
- `login` — Unique login name
- `password` — Hashed password (bcrypt)
- `active` — Boolean (disable instead of deleting)
- `action_id` — Many2one to `ir.actions.act_window` (home action)
- `sel_groups_*` — Many2many fields for categorical group selection

## Common Methods
- `_check_implicit_login()` — Validate unique login
- `action_show_groups()` — Open groups configuration
- `write()` — Overrides password hashing
- `preference_save()` — Save frontend preferences

## Inheritance Patterns

```python
class ResUsers(models.Model):
    _inherit = "res.users"

    def _compute_my_field(self):
        """Override user compute for additional fields"""
```

## Security
- Never expose password fields in API
- Use `sudo()` sparingly — users have elevated privileges
- `check_access_rights('write')` validates write permission

## Known Pitfalls
- `sudo()` on `res.users` is dangerous — prefer `check_access_rights()`
- User records are eagerly loaded; avoid `self.env.user` in loops
- Don't delete users — set `active = False`
- `partner_id` changes affect both models
