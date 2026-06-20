---
name: knowledge-res-partner
model: res.partner
module: base
priority: high
tags:
  - knowledge
  - contacts
  - base
---

# res.partner — Partner (Customer, Vendor, Contact)

## Purpose

Universal contact model used across all Odoo modules. Represents customers, vendors, companies, individual contacts, and delivery addresses.

## Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | Char | Partner name (company or contact) |
| `company_type` | Selection | `company` or `person` |
| `parent_id` | Many2one (`res.partner`) | Parent company (for contacts) |
| `child_ids` | One2many (`res.partner`) | Contacts under this company |
| `email` | Char | Primary email |
| `phone` | Char | Phone number |
| `mobile` | Char | Mobile number |
| `street`, `city`, `zip`, `country_id` | Address | Structured address fields |
| `vat` | Char | Tax ID / VAT number |
| `is_company` | Boolean | True if company_type = 'company' |
| `customer_rank` | Integer | > 0 if customer (auto-set) |
| `supplier_rank` | Integer | > 0 if vendor (auto-set) |
| `user_id` | Many2one (`res.users`) | Salesperson |
| `property_account_receivable_id` | Many2one (`account.account`) | AR account (property) |
| `property_account_payable_id` | Many2one (`account.account`) | AP account (property) |
| `company_id` | Many2one (`res.company`) | Multi-company |

## Key Points

- **One model for everything**: customers, vendors, contacts, delivery addresses, employees — all use `res.partner`
- **`is_company` vs `child_ids`**: Companies have child contacts. `parent_id` links a contact to its company
- **Properties**: `property_*` fields are company-dependent — can differ per company
- **Auto-detection**: `customer_rank` increments when a sales order is created; `supplier_rank` from purchase orders

## Common Queries

```python
# Find all contacts of a company
company = self.env['res.partner'].browse(company_id)
contacts = company.child_ids

# Find commercial partner (top-level company)
partner = self.env['res.partner'].browse(partner_id)
top = partner.commercial_partner_id
```

## Common Inheritance

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_tier = fields.Selection([
        ('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold'),
    ], default='bronze')

    def _commercial_fields(self):
        return super()._commercial_fields() + ['custom_tier']
```

## References

- orm-field-index
- security-record-rules-row-level
