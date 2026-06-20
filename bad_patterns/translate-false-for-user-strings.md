---
name: translate-false-for-user-strings
severity: medium
tags:
  - anti-pattern
  - i18n
  - translation
---

# Missing translate on User-Facing Fields

## ❌ Anti-Pattern

```python
class ProductCategory(models.Model):
    _name = 'product.category'

    name = fields.Char("Name")
    # Not translatable — non-English users see English names
```

## ✅ Fix

```python
class ProductCategory(models.Model):
    _name = 'product.category'

    name = fields.Char("Name", translate=True)
```

## Why It Hurts

Users in multi-language environments expect field content in their language. Fields like `name`, `description`, `note` should be translatable. Fields like `reference`, `code`, `barcode` should not.

## When to translate

| Translate=True | Translate=False |
|----------------|-----------------|
| Name, Title | Reference, Code |
| Description, Note | Barcode, Serial |
| Terms, Conditions | Technical fields |
| Label, Message | ID, Key, Slug |

## Detected When

- User-facing Char/Text field without `translate=True`
- Field named `name`, `description`, `note`, `comment` without translate
- Module targets multi-language deployments

## References

- lint-translation-methods
