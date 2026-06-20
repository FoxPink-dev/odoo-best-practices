---
priority: SHOULD
tags: [orm, naming, rec-name, name-get, name-search, display-name]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "setting record display name"
    includes: ["_rec_name", "name_get", "name_search", "_compute_display_name"]
  - task: "overriding name methods"
    includes: ["def name_get", "def name_search", "def _compute_display_name"]
---
# ORM Rec Name and Display

## Description

Set `_rec_name` on every model to indicate which field is used as the human-readable record identifier (defaults to `'name'`). If your model has no `name` field, set `_rec_name` to another Char field, or override `name_get()` for complex display logic. Override `name_search()` when the default search on `_rec_name` is insufficient. For models where multiple fields contribute to the display name, override `_compute_display_name()` instead — this is the modern approach and works with the ORM's prefetching.

## Correct

```python
from odoo import models, fields, api

class ProductProduct(models.Model):
    _name = 'product.product'
    _rec_name = 'display_name'

    # Override name_get for custom display
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.default_code}] {record.name}" if record.default_code else record.name
            result.append((record.id, name))
        return result

    # Override name_search for custom search behavior
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('default_code', '=ilike', name + '%'), ('name', operator, name)]
        return self.search(domain + args, limit=limit).name_get()

class ProductTemplate(models.Model):
    _name = 'product.template'
    _rec_name = 'name'

    name = fields.Char(required=True)
```

## Incorrect

```python
from odoo import models, fields

class ProductProduct(models.Model):
    _name = 'product.product'
    # WRONG: no _rec_name set, model has no 'name' field
    # Falls back to 'name' which doesn't exist, causing errors

    product_code = fields.Char(string="Code")
    product_name = fields.Char(string="Product Name")

    def name_get(self):
        # WRONG: reimplementing what _rec_name does
        return [(record.id, record.product_name) for record in self]
```

## Rationale

The Odoo 17.0 ORM docs specify `_rec_name` as the "field to use for labeling records, default: `name`." The automatic `display_name` field equals the `_rec_name` value by default. Overriding `name_get()` changes how records appear in dropdowns, Many2one fields, and breadcrumbs. Overriding `name_search()` controls how records are found during typing in relational field search boxes. The `_compute_display_name()` method (Odoo 16+) is the recommended way to customize display names without overriding `name_get()`. The docs also note that `name_search()` "is used for example to provide suggestions based on a partial value for a relational field."

## References

- Odoo 17.0 ORM docs: `_rec_name = None` — field to use for labeling records, default: `name`
- Odoo 17.0 ORM docs: `display_name` — equals `_rec_name` value by default
- Odoo 17.0 ORM docs: `name_get()` — returns list of (id, display_name) pairs
- Odoo 17.0 ORM docs: `name_search()` — searches for records matching display name pattern
