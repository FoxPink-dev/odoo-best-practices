---
priority: MUST
tags: [module, security, record-rules, ir-rule]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining record rules"
    includes: ["**/security/*.xml"]
  - task: "restricting record visibility"
    includes: ["**/security/*.xml"]
---

# Module Record Rules

## Description

Record rules (`ir.rule`) filter which records users can access within a model. They operate after ACLs and are evaluated record-by-record. Proper design of record rules is essential for data isolation.

## Correct

```xml
<odoo>
    <!-- Group-specific rule: users see only their own records -->
    <record id="my_model_rule_user" model="ir.rule">
        <field name="name">My Model: User sees own records only</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="groups" eval="[(4, ref('group_my_module_user'))]"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="True"/>
        <field name="perm_create" eval="True"/>
        <field name="perm_unlink" eval="False"/>
    </record>

    <!-- Manager rule: sees all records in their company -->
    <record id="my_model_rule_manager" model="ir.rule">
        <field name="name">My Model: Manager sees all company records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="groups" eval="[(4, ref('group_my_module_manager'))]"/>
        <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    </record>
</odoo>
```

## Incorrect

```xml
<!-- WRONG: no groups specified → global rule (intersects with all other rules) -->
<record id="my_model_rule_all" model="ir.rule">
    <field name="name">My Model: Restrict all</field>
    <field name="model_id" ref="model_my_model"/>
    <!-- Missing groups="" → this becomes a global rule -->
    <field name="domain_force">[('state', '=', 'done')]</field>
</record>

<!-- WRONG: overly broad domain that accidentally excludes records -->
<record id="my_model_rule_user" model="ir.rule">
    <field name="name">My Model: User rule</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="groups" eval="[(4, ref('group_my_module_user'))]"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>  <!-- Users should rarely delete -->
</record>
```

## Rationale

- **Group vs global rules**: Group rules (with `groups` set) are additive within the same group — if any group rule allows a record, the record is accessible. Global rules (no `groups`) are intersective — all global rules must allow the record.
- **Domain context variables**: Use `user.id` for current user, `company_id` for current company ID, `company_ids` for all accessible companies, `time` for Python's time module.
- **Operation flags**: Use `perm_read`, `perm_write`, `perm_create`, `perm_unlink` to apply rules only to specific operations. All default to `True` (applies to all operations).
- **Naming convention**: `{Model}: {Role} sees {scope}` — descriptive names help debugging.
- **Performance**: Complex record rule domains with many OR conditions can slow down queries. Prefer simple domains over deeply nested ones.
- **Admin bypass**: Administrator users (group `base.group_erp_manager`) bypass all record rules.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
