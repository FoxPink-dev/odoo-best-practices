---
priority: SHOULD
tags: [security, check-access-rights, check-access-rules]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "programmatically checking permissions"
    includes: ["**/*.py"]
  - task: "implementing access control in code"
    includes: ["**/models/*.py"]
---

# Security: `check_access_rights` and `check_access_rule` Usage

## Description

Odoo provides programmatic methods to check user permissions: `check_access_rights()` (ACL check) and `check_access_rule()` (record rule check). These should be used in custom controllers, RPC methods, and complex business logic to validate permissions explicitly.

## Correct

```python
from odoo.exceptions import AccessError


class MyModel(models.Model):
    _name = 'my.model'

    def action_sensitive_operation(self):
        """Perform a sensitive operation with explicit access check."""
        # Check ACL: does the user have write access to this model?
        self.check_access_rights('write')

        # Check record rules: can the user write these specific records?
        self.check_access_rule('write')

        # Proceed with operation
        for record in self:
            record._do_sensitive_work()

    @api.model
    def api_create_record(self, **kwargs):
        """Controller-facing method with explicit permission check."""
        if not self.env.user.has_group('my_module.group_my_module_manager'):
            raise AccessError(_("Only managers can create records via API."))

        # Also check standard ACL
        self.check_access_rights('create')
        return self.create(kwargs)
```

```python
# In a controller
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    @http.route('/api/my_model/<int:record_id>', type='json', auth='user')
    def get_record(self, record_id):
        """API endpoint with explicit access checks."""
        record = request.env['my.model'].sudo().browse(record_id)
        if not record.exists():
            return {'error': 'Not found'}

        # Explicit check: is the current user allowed to read this record?
        try:
            record.sudo().check_access_rule('read')
        except AccessError:
            return {'error': 'Access denied'}

        # Return data (using sudo() + check so the read succeeds but is validated)
        return record.sudo().read(['name', 'state'])
```

## Incorrect

```python
# WRONG: bypassing security checks entirely
def action_process(self):
    """Process without any permission check."""
    # Any user who can call this can process any record
    for record in self:
        record._process()

# WRONG: assuming check is unnecessary because of record rules
def action_delete(self):
    """Delete without explicit check."""
    self.unlink()
    # If this is called from a method that bypasses standard button behavior,
    # record rules may not be evaluated properly.

# WRONG: checking ACL but not record rules
def action_update(self):
    self.check_access_rights('write')  # Only checks model-level ACL
    self.write({'state': 'done'})       # Record rules may still block this
```

## Rationale

- **`check_access_rights(operation)`**: Checks model-level ACLs for the given operation (`read`, `write`, `create`, `unlink`). Raises `AccessError` if the user lacks permission.
- **`check_access_rule(operation)`**: Checks record rules for the given operation on each record. Raises `AccessError` if any rule blocks access.
- ORM methods (`search`, `read`, `write`, `unlink`) call these internally. Explicit checks are needed in:
  - `sudo()` blocks (to re-assert the user's permissions)
  - Controller endpoints
  - External API methods
  - Methods that aggregate records across different users
- **Pattern with `sudo()`**: Use `record.sudo().check_access_rule('read')` to check the current user's permission on a record fetched with sudo, then `record.sudo().read()` to read while respecting the earlier check.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
- Odoo ORM: https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html
