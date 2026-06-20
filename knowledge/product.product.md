---
name: knowledge-product-product
model: product.product
module: product
priority: high
tags:
  - knowledge
  - products
  - inventory
---

# product.product — Product Variant

## Purpose

Represents individual product variants (SKUs). Every sellable/purchasable/manufacturable item is a `product.product`. The template is `product.template`.

## Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | Char | Product name (inherited from template) |
| `default_code` | Char | Internal reference / SKU |
| `barcode` | Char | Barcode / EAN |
| `product_tmpl_id` | Many2one (`product.template`) | Parent template |
| `categ_id` | Many2one (`product.category`) | Category (from template) |
| `list_price` | Float | Sales price |
| `standard_price` | Float | Cost price (costing method dependent) |
| `type` | Selection | `consu` (consumable), `service`, `product` (storable) |
| `uom_id` | Many2one (`uom.uom`) | Unit of measure |
| `uom_po_id` | Many2one (`uom.uom`) | Purchase UOM |
| `tracking` | Selection | `none`, `lot` (batch), `serial` (unique) |
| `qty_available` | Float | Current stock (computed, context-dependent) |
| `virtual_available` | Float | Forecast stock (computed) |
| `sale_ok` | Boolean | Can be sold |
| `purchase_ok` | Boolean | Can be purchased |
| `active` | Boolean | Active (archived if False) |

## Product Template vs Product

```
product.template (1) ── has variants ──> product.product (N)
     │                                         │
     │ name, description, list_price           │ default_code, barcode, standard_price
     │ categ_id, type                          │ qty_available
     │ sale_ok, purchase_ok                    │ (variant-specific)
```

## Common Methods

| Method | Description |
|--------|-------------|
| `_compute_quantities()` | Computes stock quantities |
| `price_compute()` | Computes price based on pricelist |
| `_get_domain_price()` | Domain for price computation |

## Common Inheritance

```python
class ProductProduct(models.Model):
    _inherit = 'product.product'

    custom_stock_field = fields.Float(
        compute='_compute_custom_stock', store=True
    )

    @api.depends('qty_available', 'type')
    def _compute_custom_stock(self):
        for record in self:
            if record.type == 'product':
                record.custom_stock_field = record.qty_available
```

## Known Pitfalls

- `qty_available` is context-dependent (warehouse) — use `with_context(warehouse=x)`
- Tracking changes require stock moves to be completed first
- `standard_price` update doesn't retroactively change COGS

## References

- perf-computed-dependencies
- orm-no-n-plus-1
