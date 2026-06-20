---
name: no-acl-for-new-model
severity: critical
tags:
  - anti-pattern
  - security
  - acl
---

# Missing ACL for New Model

## ❌ Anti-Pattern

```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Custom Model'
```
```xml
<!-- NO security/ir.model.access.csv -->
```

## ✅ Fix

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

## Why It Hurts

Without ACL, only the superuser can access the model. Every non-admin user gets an `AccessError`. This is the #1 support issue for new Odoo modules.

## Detected When

- New `models.Model` subclass defined
- No corresponding entry in `security/ir.model.access.csv`
- Error: `AccessError - Sorry, you are not allowed to access this document`

## References

- security-acl-required
