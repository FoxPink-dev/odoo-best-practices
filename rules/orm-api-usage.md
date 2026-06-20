---
priority: MUST
tags: [orm, api, search, browse, create, write, unlink]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "querying records"
    includes: ["search\(", "browse\(", "search_count\(", "search_read\("]
  - task: "modifying records"
    includes: ["\\.create\(", "\\.write\(", "\\.unlink\(", "\\.copy\("]
  - task: "reading field values"
    includes: ["\\.read\(", "\\.mapped\(", "\\.name_get\("]
  - task: "data operations"
    includes: ["for.*in.*\\:", "search\(", "browse\("]
---
# ORM API Usage

## Description

Use the correct ORM method for each operation: `search()` for record lookup by domain, `browse()` when IDs are already known, `search_count()` when only a count is needed, `search_read()` when only specific fields are needed (avoids loading full recordsets), and `mapped()` for efficient field extraction across a recordset. Bulk operations (`create` with list of dicts, `write` on recordsets) are always preferred over per-record loops.

## Correct

```python
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_active_customer_count(self):
        # Use search_count when only the count is needed
        return self.search_count([('customer_rank', '>', 0), ('active', '=', True)])

    def get_partner_names(self):
        # Use search_read when only specific fields are needed
        return self.search_read(
            [('customer_rank', '>', 0)],
            ['name', 'email'],
            limit=100
        )

    def archive_partners(self, partner_ids):
        # Browse once with collected IDs, then write on the recordset
        partners = self.browse(partner_ids)
        partners.write({'active': False})

    def bulk_create_from_list(self, data_list):
        # Bulk create with a list of dicts
        return self.create([{'name': d['name'], 'email': d['email']} for d in data_list])
```

## Incorrect

```python
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_active_customer_count(self):
        # WRONG: loads full records into memory just for a count
        partners = self.search([('customer_rank', '>', 0), ('active', '=', True)])
        return len(partners)

    def get_partner_names(self):
        # WRONG: search then iterate to read fields
        partners = self.search([('customer_rank', '>', 0)])
        result = []
        for partner in partners:
            result.append({'name': partner.name, 'email': partner.email})
        return result

    def archive_partners(self, partner_ids):
        # WRONG: browse inside a loop
        for pid in partner_ids:
            self.browse(pid).write({'active': False})

    def bulk_create_from_list(self, data_list):
        # WRONG: creates records one at a time inside a loop
        for d in data_list:
            self.create({'name': d['name'], 'email': d['email']})
```

## Rationale

The Odoo ORM documentation specifies that `search()` is the high-level method for domain-based lookup, while `browse()` is for ID-based access. Using `search_count()` instead of `len(search(...))` avoids fetching records into memory. `search_read()` combines search + read in a single optimized query. `mapped()` with a field name string is more efficient than a list comprehension because it leverages the ORM's prefetching. Bulk `create()` with a list of dicts generates a single INSERT statement. Writing on a recordset calls `write()` once; per-record assignment inside a loop triggers N separate UPDATE queries.

## References

- Odoo 17.0 ORM docs: `search()` — Search for records that satisfy the given domain
- Odoo 17.0 ORM docs: `browse()` — Returns a recordset for the ids provided
- Odoo 17.0 ORM docs: `search_count()` — Returns the number of records matching the domain
- Odoo 17.0 ORM docs: `create()` — Creates new records (accepts list of dicts)
- Odoo 17.0 ORM docs: `write()` — Updates all records in self with provided values
- Odoo 17.0 ORM docs: `mapped()` — Apply func on all records, return list or recordset
