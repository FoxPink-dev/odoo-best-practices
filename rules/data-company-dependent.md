---
name: data-company-dependent
priority: SHOULD
tags:
  - data
  - multi-company
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - create company-dependent field
  - define multi-company data
---
# data-company-dependent — Company-Dependent Data Patterns

Company-dependent fields (`company_dependent=True`) and data records scoped to `company_id` allow per-company configuration. Use them instead of duplicating models per company.

## Correct

```python
class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    internal_notes = fields.Text(
        string="Internal Notes",
        company_dependent=True,
    )
```

```xml
<!-- Company-dependent data in noupdate="1" -->
<odoo noupdate="1">
  <!-- Default internal note for all companies (company_id will be set at runtime) -->
  <record id="base_main_company" model="res.company">
    <field name="internal_notes" model="res.partner" eval="0"/>
  </record>
</odoo>
```

## Incorrect

```python
# Duplicating models per company instead of using company_dependent
class ResPartnerCompanyA(models.Model):
    _name = 'res.partner.company.a'

class ResPartnerCompanyB(models.Model):
    _name = 'res.partner.company.b'
```

## Rationale

- `company_dependent=True` fields are stored in `ir.property` and resolved per-company automatically.
- Avoid creating separate models or fields per company — it doesn't scale.
- For records that vary per company, add a `company_id` Many2one field and filter domains accordingly.
- Company-dependent data should use `noupdate="1"` so administrators can customize per-company values.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html#fields-company-dependent
- https://www.odoo.com/documentation/18.0/applications/essentials/property_fields.html
