---
priority: MUST
tags: [security, record-rules, ir-rule, row-level]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining record-level security"
    includes: ["**/security/*.xml"]
  - task: "restricting record access"
    includes: ["**/security/*.xml"]
---

# Security: Record Rule Design & Domain-Based Security

## Description

Record rules (`ir.rule`) filter records at row level using domain expressions. They operate after ACLs, restricting which specific records a user can read, write, create, or delete within a model they already have access to.

## Correct

```xml
<odoo>
    <!-- Domain restricting to own records -->
    <record id="my_model_rule_own" model="ir.rule">
        <field name="name">My Model: Own records only</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="groups" eval="[(4, ref('my_module.group_my_module_user'))]"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
    </record>

    <!-- Domain with multi-company scope -->
    <record id="my_model_rule_company" model="ir.rule">
        <field name="name">My Model: Company scope</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    </record>

    <!-- Domain filtering by state -->
    <record id="my_model_rule_draft_only" model="ir.rule">
        <field name="name">My Model: Restricted to draft</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="groups" eval="[(4, ref('my_module.group_my_module_user'))]"/>
        <field name="domain_force">[('state', '=', 'draft')]</field>
        <field name="perm_write" eval="True"/>
    </record>
</odoo>
```

## Incorrect

```xml
<!-- WRONG: overly complex domain that affects performance -->
<record id="my_model_rule_complex" model="ir.rule">
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">
        ['|', '|',
            ('user_id', '=', user.id),
            ('team_id.user_ids', 'in', [user.id]),
            ('manager_id', '=', user.id),
        ]
    </field>
</record>

<!-- WRONG: domain_force with hardcoded IDs that break across databases -->
<record id="my_model_rule_bad" model="ir.rule">
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', 1)]</field>
</record>

<!-- WRONG: rule without any perm_ flags → applies to all operations -->
<record id="my_model_rule_no_perm" model="ir.rule">
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('state', '=', 'done')]</field>
    <!-- Should use perm_read/write/create/unlink to scope -->
</record>
```

## Rationale

- **Default-allow**: Record rules are default-allow. If no rule applies, access is granted (based on ACLs).
- **Domain variables**: `user.id` (current user ID), `company_id` (current company), `company_ids` (all user companies), `time` (Python time module).
- **Operation scoping**: Use `perm_read`, `perm_write`, `perm_create`, `perm_unlink` to apply rules to specific operations only.
- **Performance**: Avoid M2O/O2M traversals in domains where possible. Complex relational domains can slow down queries significantly.
- **Naming**: Convention: `{Model}: {Role} sees {scope}`. Descriptive names help debugging access issues.
- **Administrator bypass**: Users in `base.group_erp_manager` bypass all record rules.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
