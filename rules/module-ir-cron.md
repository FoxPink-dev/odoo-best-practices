---
priority: SHOULD
tags: [module, cron, scheduled-actions, ir-cron]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating scheduled actions"
    includes: ["**/data/*.xml"]
  - task: "editing ir.cron records"
    includes: ["**/*.xml"]
---

# Module Scheduled Actions (ir.cron)

## Description

Scheduled actions (`ir.cron`) define periodic tasks in Odoo. They must be properly configured with correct intervals, user contexts, and error handling to avoid performance degradation or silent failures.

## Correct

```xml
<odoo noupdate="1">
    <record id="ir_cron_my_model_cleanup" model="ir.cron">
        <field name="name">My Model: Cleanup expired records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="state">code</field>
        <field name="code">model._cleanup_expired_records()</field>
        <field name="user_id" ref="base.user_root"/>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="numbercall">-1</field>
        <field name="doall" eval="False"/>
        <field name="active" eval="True"/>
    </record>
</odoo>
```

```python
class MyModel(models.Model):
    _name = 'my.model'

    def _cleanup_expired_records(self):
        """Cleanup method called by cron - safe for batch processing."""
        expired = self.search([
            ('expiry_date', '<', fields.Datetime.now()),
            ('state', '=', 'active'),
        ])
        expired.write({'state': 'expired'})
        _logger.info("Expired %d records in My Model", len(expired))
```

## Incorrect

```python
# WRONG: cron method without proper error handling
def _cleanup_expired_records(self):
    for record in self.search([('expiry_date', '<', fields.Datetime.now())]):
        # Raises exception if any record fails, stopping the entire cron
        record.action_expire()

# WRONG: heavy computation in cron that blocks the scheduler
def _nightly_report(self):
    # Generates report for ALL records every minute
    # Should be batched or deferred
    all_records = self.search([])
    for record in all_records:
        record._generate_report()
```

## Rationale

- Always wrap cron records in `<odoo noupdate="1">` so users can customize intervals without overwrite on upgrade.
- Use `model_id` and `code` (calling a method) over `model_id` with `function` approach for cleaner code.
- Set `user_id` to `base.user_root` unless the method needs specific user permissions.
- Use `numbercall = -1` for recurring (infinite) tasks. Use a positive integer for one-shot or finite-count tasks.
- Set `doall = False` so missed executions are not replayed on server restart.
- Cron methods should be idempotent, handle exceptions gracefully, and include logging.
- For long-running operations, process records in batches using `search()` with limit/offset.

## References

- Odoo 17.0 Module Manifests: https://www.odoo.com/documentation/17.0/developer/reference/backend/module.html
