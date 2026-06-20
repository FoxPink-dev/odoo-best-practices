---
name: i18n-translatable-fields
priority: SHOULD
tags:
  - i18n
  - fields
  - translate
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - define char field
  - define text field
  - define html field
---
# i18n-translatable-fields — `translate=True` Field Usage

Fields containing user-visible text should use `translate=True` so values can be stored per-language. Apply it to `Char`, `Text`, and `Html` fields that hold end-user content.

## Correct

```python
class ProductTemplate(models.Model):
    _name = 'product.template'

    name = fields.Char(translate=True, required=True)
    description_sale = fields.Text(translate=True)
    description_purchase = fields.Text(translate=True)
    website_description = fields.Html(translate=True, sanitize=True)

class SaleOrder(models.Model):
    _name = 'sale.order'

    note = fields.Text(translate=True)  # Internal note visible to users
```

## Incorrect

```python
class ProductTemplate(models.Model):
    _name = 'product.template'

    # Hardcoded English-only field
    name = fields.Char()

    # Technical field that should NOT be translated
    internal_code = fields.Char(translate=True)
```

## Rationale

- Fields with `translate=True` store translations in `ir.translation` and are resolved per user language.
- Apply `translate=True` to any field whose value is directly displayed to end users: names, descriptions, notes, help text.
- Do NOT apply to technical fields: codes, references, slugs, JSON payloads, computed fields with deterministic values.
- `translate=True` on Html fields enables per-language rich text content.
- Be aware: `translate=True` fields cannot be used in `ORDER BY` or searched across languages efficiently at scale.
- When overriding a translatable field via inheritance, ensure `translate` is preserved or explicitly set.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html#fields-translate
