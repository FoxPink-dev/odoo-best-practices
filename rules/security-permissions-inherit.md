---
priority: SHOULD
tags: [security, permissions, inherit, delegation]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "inheriting security from parent models"
    includes: ["**/models/*.py", "**/security/*.xml"]
  - task: "using delegation or inheritance"
    includes: ["**/models/*.py"]
---

# Security: Inheriting Security from Parent Models

## Description

When using model inheritance (`_inherit`), the child model does NOT automatically inherit the parent's ACLs or record rules. Security must be explicitly defined for each model. However, with `_inherits` (delegation inheritance), some security considerations differ.

## Correct

```python
# Standard inheritance: child model needs its own ACLs
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = 'mail.thread'
    _description = 'My Model'
    # ACLs must be defined separately in ir.model.access.csv
    # model_my_model needs its own access entries
```

```python
# Delegation inheritance: child delegates fields to parent
class LibraryBook(models.Model):
    _name = 'library.book'
    _inherits = {'product.product': 'product_id'}
    _description = 'Library Book'
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade',
    )
    isbn = fields.Char(string='ISBN')
    # Security: ACLs on library.book control base access.
    # product.product ACLs also apply to the delegated fields.
```

```csv
# ACLs for inherited model MUST still be defined
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,my_module.group_my_module_user,1,1,0,0
```

```python
# Inheriting record rules from parent via mapping
class MyModel(models.Model):
    _name = 'my.model'

    def check_access_rule(self, operation):
        """Extend parent record rule check if needed."""
        # Parent model record rules are NOT automatically applied
        # Do custom logic if parent rules must be honored
        return super().check_access_rule(operation)
```

## Incorrect

```python
# WRONG: assuming _inherit models share ACLs
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = 'mail.thread'
    # No ACL defined for my.model in CSV
    # → Only admin can access this model!

# WRONG: _inherits without ACL on child model
class LibraryBook(models.Model):
    _name = 'library.book'
    _inherits = {'product.product': 'product_id'}
    # No ACL for library.book
    # → Even though product.product has ACLs, library.book does not inherit them.
```

## Rationale

- **Standard inheritance** (`_inherit`): The child model is a completely separate table. It must have its own ACL entries and can have its own record rules. Parent ACLs are NOT inherited.
- **Delegation inheritance** (`_inherits`): The child model stores a reference to the parent. The child needs its own ACLs for its own model, but the parent's ACLs govern the parent fields. The child's record rules determine visibility of child records.
- **`_inherit` vs `_inherits`**:
  - `_inherit`: Child extends parent (same table if using `_name` from parent, or new table if new `_name`).
  - `_inherits`: Child delegates field access to parent record (composition pattern).
- When a model is created purely as a mixin (no `_name`), it needs no ACLs — but the models that `_inherit` it with a `_name` do.
- Record rules on parent models do NOT automatically apply to child models. If you need the same restrictions, define them explicitly on each model.
- **`_check_company`**: Models using `_inherits` should implement `_check_company` to validate company consistency between parent and child.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
- Odoo ORM: https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html
