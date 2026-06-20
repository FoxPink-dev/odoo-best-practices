---
name: security-record-rules-row-level
priority: high
tags:
  - security
  - record-rules
  - row-level
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - restrict access
  - data isolation
  - multi-company
---

# security-record-rules-row-level — Record Rules for Row-Level Security

Access rights (ACL) are model-level. Record rules (`ir.rule`) provide row-level filtering via domain expressions. Both layers must pass.

## Incorrect

```python
# Using sudo() everywhere instead of proper record rules
def action_view_orders(self):
    orders = self.env['sale.order'].sudo().search([('partner_id', '=', self.id)])
```

## Correct

```xml
<record id="rule_sale_order_own" model="ir.rule">
    <field name="name">Sale Order: Own Records</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
    <field name="domain_force">
        [('user_id', '=', user.id)]
    </field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

## Common Record Rule Patterns

| Pattern | Domain | Use Case |
|---------|--------|----------|
| User-based | `[('user_id', '=', user.id)]` | Own records only |
| Company-based | `[('company_id', 'in', company_ids)]` | Multi-company isolation |
| Team-based | `['\|', ('user_id', '=', user.id), ('team_id.member_ids', 'in', [user.id])]` | Team access |
| Department | `[('department_id.manager_id', '=', user.id)]` | Manager sees department |

## Global vs Group Rules

| Type | Combination | Effect |
|------|-------------|--------|
| Global rules | **Intersect** (AND) | Always restrict further |
| Group rules | **Unify** (OR) | Can expand access |
| Global × Group | Global ∩ (Group₁ ∪ Group₂) | Group rules can't exceed global bounds |

## Why

- ACL controls _if_ a model is accessible; record rules control _which records_
- Without record rules, all users in a group see all records
- Critical for multi-company isolation, data privacy, and compliance (SOC 2, GDPR)

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html
