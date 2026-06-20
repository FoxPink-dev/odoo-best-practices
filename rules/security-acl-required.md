---
name: security-acl-required
priority: high
tags:
  - security
  - acl
  - access-rights
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - new model
  - create model
  - define access
---

# security-acl-required — Every Model Needs ACL

Every model **must** have an ACL entry in `ir.model.access.csv`. Without it, no user (except superuser) can access the model at all.

## Incorrect

```csv
# Missing ACL for my_module.my_model
# → Users get AccessError on any operation
```

## Correct

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

## Patterns

| Group | Read | Write | Create | Unlink | Use case |
|-------|------|-------|--------|--------|----------|
| `base.group_user` (Employee) | 1 | 1 | 1 | 0 | Standard CRUD, no delete |
| `base.group_portal` (Portal) | 1 | 0 | 0 | 0 | Read-only for portal users |
| `base.group_public` (Public) | 0 | 0 | 0 | 0 | No access |
| Custom group | 1 | 1 | 1 | 1 | Full access for managers |

## Why

- ACL is the first gate: no ACL = no access, regardless of record rules
- ACL is model-level, record rules are row-level — both must pass
- Without ACL, even `sudo()` is needed which is a code smell

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html
