---
priority: SHOULD
tags: [module, actions, server-actions, automated-actions]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating server or automated actions"
    includes: ["**/data/*.xml"]
  - task: "editing ir.actions.server records"
    includes: ["**/*.xml"]
---

# Module Server Actions & Automated Actions

## Description

Server actions (`ir.actions.server`) and automated actions (`base.action.rule`) allow executing Python code, sending emails, or updating records in response to triggers. They must be carefully designed for maintainability and debuggability.

## Correct

```xml
<odoo noupdate="1">
    <!-- Server action that calls a model method -->
    <record id="action_server_my_model_validate" model="ir.actions.server">
        <field name="name">Validate My Model</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="state">code</field>
        <field name="code">
            records.action_validate()
        </field>
    </record>

    <!-- Automated action: trigger on create/update -->
    <record id="automated_action_my_model_assign" model="base.action.rule">
        <field name="name">My Model: Auto-assign on create</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="kind">on_create</field>
        <field name="filter_pre_domain">[('user_id', '=', False)]</field>
        <field name="server_action_ids" eval="[(4, ref('action_server_my_model_assign'))]"/>
        <field name="active" eval="True"/>
    </record>
</odoo>
```

```python
class MyModel(models.Model):
    _name = 'my.model'

    def action_validate(self):
        """Called from server action - validates and transitions state."""
        for record in self:
            record.write({'state': 'validated', 'validated_date': fields.Datetime.now()})
        return True
```

## Incorrect

```xml
<!-- WRONG: inline Python code in XML instead of a model method -->
<field name="code">
    for record in records:
        record.write({'state': 'validated'})
        template = self.env.ref('my_module.email_template_validation')
        template.send_mail(record.id)
</field>

<!-- WRONG: automated action without pre-filter (runs on every record change) -->
<record id="automated_action_my_model_all" model="base.action.rule">
    <field name="name">My Model: Process all</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="kind">on_create_or_write</field>
    <!-- Missing filter_pre_domain → triggers on every create/write -->
</record>
```

## Rationale

- **Prefer model methods over inline code**: Server action `code` should call a single method (e.g., `records.action_validate()`). This makes the logic testable, refactorable, and traceable.
- **Automated action types**: Use `on_create` for creation-only triggers, `on_write` for update-only, `on_create_or_write` for both, and `on_time` for time-based (not directly — use `ir.cron` instead).
- **Pre-filters**: Always set `filter_pre_domain` to limit when the automated action runs. This avoids unnecessary evaluations and potential infinite loops.
- **`noupdate="1"`**: Server actions and automated actions should be `noupdate="1"` so user customizations survive upgrades.
- **Testing**: Complex automated actions should be tested; they are a common source of performance issues and unexpected side effects.

## References

- Odoo 17.0 Actions: https://www.odoo.com/documentation/17.0/developer/reference/backend/actions.html
