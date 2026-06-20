---
name: security-least-privilege
priority: high
tags:
  - security
  - groups
  - permissions
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - define groups
  - setup permissions
  - design roles
---

# security-least-privilege — Grant Minimum Permissions

Every user should have the minimum access required to perform their job. Start from zero and grant explicitly.

## Incorrect

```csv
# Giving all internal users full CRUD on sensitive data
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_hr_contract_all,hr.contract.all,model_hr_contract,base.group_user,1,1,1,1
access_payroll_all,hr.payslip.all,model_hr_payslip,base.group_user,1,1,1,1
```

## Correct

```xml
<!-- Create specific groups with graduated permissions -->
<record id="group_hr_contract_user" model="res.groups">
    <field name="name">Contract User</field>
    <field name="category_id" ref="base.module_category_human_resources"/>
</record>

<record id="group_hr_contract_manager" model="res.groups">
    <field name="name">Contract Manager</field>
    <field name="category_id" ref="base.module_category_human_resources"/>
    <field name="implied_ids" eval="[(4, ref('group_hr_contract_user'))]"/>
</record>
```

```csv
# Contract User: read-only
access_hr_contract_user,hr.contract.user,model_hr_contract,group_hr_contract_user,1,0,0,0
# Contract Manager: full access
access_hr_contract_manager,hr.contract.manager,model_hr_contract,group_hr_contract_manager,1,1,1,1
```

## Permission Levels

| Level | Read | Write | Create | Unlink | Typical Role |
|-------|------|-------|--------|--------|-------------|
| None | 0 | 0 | 0 | 0 | Public / Portal |
| Read-only | 1 | 0 | 0 | 0 | Viewers, auditors |
| User | 1 | 1 | 1 | 0 | Regular employees |
| Manager | 1 | 1 | 1 | 1 | Team leads, admins |

## Security Review Checklist

- Each group has a documented purpose
- Groups form a hierarchy with `implied_ids`
- ACL uses custom groups, not `base.group_user` for sensitive models
- No group grants more than needed for its role
- Record rules further restrict row-level access per user

## Why

- Limits blast radius of compromised accounts
- Simplifies compliance audits (SOC 2, GDPR)
- Default Odoo is too permissive — internal users see HR, CRM, accounting data by default

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html
