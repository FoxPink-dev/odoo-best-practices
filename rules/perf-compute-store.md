---
priority: SHOULD
tags: [performance, computed-fields, store, orm]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining computed fields"
    includes: ["models/*.py"]
---
# Performance Compute Store

## Description

Use `store=True` on computed fields that are frequently searched, grouped, or displayed in list views. Non-stored computed fields (`store=False`, the default) are computed on-the-fly each time they are accessed. Store when: the field is used in domains, `group_by`, `order`, or is expensive to compute. Never store when: the field depends on volatile data or is rarely accessed. Always list all dependencies in `@api.depends`.

## Correct

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    # Stored: frequently searched/grouped
    amount_total = fields.Monetary(
        compute='_compute_amount_total', store=True,
    )
    amount_untaxed = fields.Monetary(
        compute='_compute_amount_untaxed', store=True,
    )

    @api.depends('order_line.price_subtotal', 'order_line.tax_id')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(
                line.price_subtotal + line.price_tax
                for line in order.order_line
            )

    # Non-stored: rarely accessed, cheap to compute
    display_summary = fields.Char(compute='_compute_summary')

    @api.depends('name', 'partner_id.name')
    def _compute_summary(self):
        for record in self:
            record.display_summary = f"{record.name} - {record.partner_id.name}"
```

## Incorrect

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    # Non-stored but searched frequently - very slow
    amount_total = fields.Monetary(compute='_compute_amount_total')

    @api.depends('order_line.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.order_line.mapped('price_subtotal'))

    def search_orders(self):
        # This triggers compute for ALL orders - extremely slow
        return self.search([('amount_total', '>', 1000)])
```

## Rationale

Stored fields are pre-computed and stored in the database, making search/group/sort fast at the cost of write amplification (recomputed on dependency change). Non-stored fields compute on every access and cannot be searched or grouped. A common pattern: store aggregate fields (totals, counts) and leave lightweight string/display fields non-stored. When in doubt, profile with `--log-sql`.

## References

- Odoo 17.0 ORM docs: "Computed Fields" section
- Odoo 17.0 ORM docs: `compute`, `store`, `@api.depends` attributes
