---
priority: MUST
tags: [security, ir-rule, global-rules, group-rules]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining global vs group record rules"
    includes: ["**/security/*.xml"]
  - task: "reviewing record rule composition"
    includes: ["**/security/*.xml"]
---

# Security: Global vs Non-Global Record Rules

## Description

Record rules can be **global** (no `groups` specified) or **group-specific** (one or more groups specified). These two types compose differently: global rules _intersect_, while group rules are additive within the same group. Understanding this distinction is critical for correct security design.

## Correct

```xml
<!-- GLOBAL rule: applies to ALL users, intersects with other global rules -->
<record id="my_model_global_company" model="ir.rule">
    <field name="name">My Model: Company isolation (global)</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <!-- No groups → global rule -->
</record>

<!-- GROUP rule: applies only to specific group -->
<record id="my_model_group_own" model="ir.rule">
    <field name="name">My Model: Own records only (user group)</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="groups" eval="[(4, ref('my_module.group_my_module_user'))]"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>

<!-- GROUP rule: manager sees all -->
<record id="my_model_group_manager" model="ir.rule">
    <field name="name">My Model: All records (manager group)</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="groups" eval="[(4, ref('my_module.group_my_module_manager'))]"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <!-- (1, '=', 1) = always true, manager sees all records -->
</record>
```

## Incorrect

```xml
<!-- WRONG: global rule that should be group-specific -->
<record id="my_model_restrict_own" model="ir.rule">
    <field name="name">My Model: Own records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <!-- No groups → this is GLOBAL, meaning ALL users can only see their own records,
         including managers who need to see all records -->
</record>

<!-- WRONG: relying only on group rules for company isolation -->
<!-- If group rules are the only company isolation, a user in two groups
     can see records from either group's scope -->
</record>

<!-- WRONG: using global=False explicitly when groups is empty -->
<record id="my_model_rule" model="ir.rule">
    <field name="name">My Model: Rule</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="global" eval="False"/>
    <!-- global=False with no groups means this rule does nothing -->
</record>
```

## Rationale

| Aspect | Global Rule | Group Rule |
|--------|-------------|------------|
| **Applies to** | All users | Only specified group(s) |
| **Composition** | Intersect (AND) | Additive within group (OR) |
| **Use case** | Multi-company, data isolation | Role-based restrictions |
| **Bypass** | Cannot be bypassed by other rules | Bypassed by other groups' rules |

- **Global rules compose by intersection**: if two global rules exist for the same model, a record must satisfy BOTH rules to be accessible. This makes global rules ideal for mandatory restrictions like company isolation.
- **Group rules compose by union**: if a user belongs to groups with different rules, the user can access records matching ANY of their group rules. This makes group rules ideal for role-based access (e.g., User sees own records, Manager sees all).
- **Never use global rules for role-based access**: A global rule restricting to own records would also restrict managers. Instead, use a group rule for the user role and a separate group rule (or no rule) for the manager role.
- **Multi-company is always a global rule**: Company data isolation must use global rules to ensure it cannot be bypassed.
- **The `global` field** is computed based on `groups` being set. Setting it explicitly is not recommended.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
