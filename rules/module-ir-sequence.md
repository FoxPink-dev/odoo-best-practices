---
priority: SHOULD
tags: [module, sequence, ir-sequence, numbering]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating sequences for models"
    includes: ["**/data/*.xml"]
  - task: "implementing auto-numbering"
    includes: ["**/models/*.py"]
---

# Module Sequence Numbering Patterns

## Description

Sequence records (`ir.sequence`) provide automatic numbering for documents like orders, invoices, and tickets. They must follow consistent patterns for prefix, padding, and reset behavior.

## Correct

```xml
<odoo noupdate="1">
    <record id="seq_my_model" model="ir.sequence">
        <field name="name">My Model</field>
        <field name="code">my.model</field>
        <field name="prefix">MM/%(year)s/</field>
        <field name="padding">5</field>
        <field name="company_id" eval="False"/>
    </record>
</odoo>
```

```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(string='Number', required=True, copy=False, default='New')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('my.model') or 'New'
        return super().create(vals_list)
```

## Incorrect

```python
# WRONG: computing sequence in compute method (called too often)
name = fields.Char(string='Number', compute='_compute_name', store=True)
@api.depends('create_date')
def _compute_name(self):
    for record in self:
        record.name = self.env['ir.sequence'].next_by_code('my.model')

# WRONG: overriding create without handling multi-record creation
@api.model
def create(self, vals):
    if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals)  # Doesn't handle create(values_list)
```

## Rationale

- Always wrap sequences in `<odoo noupdate="1">` to prevent overwriting user-customized sequences on upgrades.
- The `code` field links the sequence to `next_by_code()` calls. Choose a unique, descriptive code (convention: `<model_name>`).
- Use `padding` to set minimum digit length (typically 5).
- Use `prefix` with interpolation variables: `%(year)s`, `%(month)s`, `%(day)s`, `%(y)s`.
- Set `company_id` to `False` for sequences shared across companies, or omit for company-specific sequences.
- Override `create()` to assign sequence numbers automatically. Use `@api.model_create_multi` (v16+) or handle the singleton case properly.
- The `default='New'` pattern is the Odoo standard for sequences; it provides a readable default before the real number is assigned.

## References

- Odoo 17.0 Data Files: https://www.odoo.com/documentation/17.0/developer/reference/backend/data.html
