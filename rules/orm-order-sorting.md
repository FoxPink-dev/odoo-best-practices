---
priority: SHOULD
tags: [orm, sorting, _order, ordering]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "setting default sort order"
    includes: ["_order"]
  - task: "sorting recordsets"
    includes: ["sorted\(", "\\.sorted", "order\\s*="]
  - task: "custom ordering"
    includes: ["_order\\s*="]
---
# ORM Order and Sorting

## Description

Set `_order` on every model to define the default sort order for search results. The default is `'id'` (oldest first), which is rarely useful for business display. Use a meaningful field like a sequence number, date, or name. For multi-field sorting, list fields separated by commas. Use `DESC` for descending order. Always index fields used in the `_order` clause to avoid full table sorts. Use `sorted()` on recordsets for occasional in-memory sorting that deviates from the default.

## Correct

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'
    _order = 'date_order DESC, name ASC'

    name = fields.Char(index=True)
    date_order = fields.Datetime(index=True)

class ResPartner(models.Model):
    _name = 'res.partner'
    _order = 'display_name'

class ProductCategory(models.Model):
    _name = 'product.category'
    _parent_store = True
    _parent_name = 'parent_id'
    _order = 'sequence, name'

    sequence = fields.Integer(index=True)
    parent_id = fields.Many2one('product.category', index=True)
    parent_path = fields.Char(index=True)

    def get_sorted_children(self):
        return self.sorted(key=lambda r: r.sequence)
```

## Incorrect

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'
    _order = 'id'  # WRONG: default — not useful for business display

class ProductCategory(models.Model):
    _name = 'product.category'
    _order = 'name'  # WRONG: categories need sequence-based ordering
```

## Rationale

The Odoo 17.0 ORM docs define `_order` as the "default order field for searching results" with a default of `'id'`. Using the default means records appear in creation order, which is rarely meaningful. Multi-field sorting with `DESC` is supported: `'date_order DESC, name ASC'`. Fields in `_order` without proper database indexes cause performance issues on large tables. For hierarchical models with `_parent_store`, sort by `sequence` to allow manual reordering in the UI. The `sorted()` method on recordsets accepts a key function or field name and supports `reverse`.

## References

- Odoo 17.0 ORM docs: `_order = 'id'` — default order field for searching results
- Odoo 17.0 ORM docs: `sorted()` — returns recordset ordered by key
- Odoo 17.0 ORM docs: `search()` — supports `order` parameter to override `_order`
