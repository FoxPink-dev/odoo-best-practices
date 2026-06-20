---
priority: MUST
tags: [security, acl, access-rights, ir-model-access]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating model access rights"
    includes: ["**/security/ir.model.access.csv"]
  - task: "adding new model without ACL"
    includes: ["**/models/*.py"]
---

# Security: Model Access Rights (ir.model.access)

## Description

Access rights (ACLs) define CRUD permissions per model and per user group. They are the first security layer, controlling whether a user can perform any operation on a model at all. Every new model MUST have at least one ACL entry.

## Correct

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,my_module.group_my_module_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_my_module_manager,1,1,1,1
access_my_model_portal,my.model.portal,model_my_model,base.group_portal,1,0,0,0
access_my_model_all,my.model.all,model_my_model,,1,0,0,0
```

```xml
<!-- Alternative: XML record syntax (when complex conditions needed) -->
<record id="access_my_model_user" model="ir.model.access">
    <field name="name">my.model.user</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="group_id" ref="my_module.group_my_module_user"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

## Incorrect

```csv
# WRONG: empty group_id without understanding implications
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_all,my.model.all,model_my_model,,1,1,1,1
# Empty group_id = every user (including portal/public) gets full CRUD!

# WRONG: missing ACL for a new model (model is invisible to all non-admin users)
# No entry at all for model_my_model

# WRONG: user with full delete access unnecessarily
access_my_model_user,my.model.user,model_my_model,my_module.group_my_module_user,1,1,1,1
# Regular users rarely need delete permissions
```

## Rationale

- Every model (except `transient`/`abstract`) needs at least one ACL entry. Without it, only administrators can access the model.
- **Empty `group_id`** grants access to all users, including portal and public. Use this sparingly and only for truly public models.
- **Additive model**: ACLs are additive — a user gets the union of all permissions from all their groups. A user in User (read+create) and Manager (write) groups will have read+create+write.
- **CSV naming convention**: Row ID pattern: `access_<model>_<role>`.
- **Least privilege**: Grant the minimum permissions needed. Users rarely need `perm_unlink`. Use record rules for fine-grained control instead of broad ACLs.
- **Order in manifest**: `ir.model.access.csv` must be the first file in the `data` list.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
