---
name: i18n-string-concat
priority: MUST
tags:
  - i18n
  - translation
  - strings
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - format string
  - build message
  - concatenate text
---
# i18n-string-concat — Avoiding String Concatenation for Translatability

String concatenation breaks translation because sentence structure differs between languages. Use `str.format()` with named placeholders instead.

## Correct

```python
from odoo import _

# Named placeholders — translators reorder freely
message = _("Dear %(customer)s, your order %(order)s totals %(amount)s") % {
    'customer': partner.name,
    'order': order.name,
    'amount': order.amount_total,
}

# Python 3 format style
message = _("Dear {customer}, your order {order} totals {amount}").format(
    customer=partner.name,
    order=order.name,
    amount=order.amount_total,
)

# Multi-line with implicit string concatenation (still one msgid)
warning = _(
    "This action will confirm the invoice for %(name)s.\n"
    "The customer will be charged %(amount)s."
) % {'name': invoice.name, 'amount': invoice.amount_total}
```

## Incorrect

```python
# Broken translation — each part translated separately
message = _("Dear ") + partner.name + _(", your order ") + order.name + _(" totals ") + str(order.amount_total)

# Using %s without named parameters
message = _("Dear %s, your order %s totals %s") % (partner.name, order.name, order.amount_total)

# f-strings break translation extraction
message = _(f"Dear {partner.name}, your order {order.name} totals {order.amount_total}")

# HTML concatenation
message = _("<b>Dear</b> ") + partner.name + _(" <b>your order</b> ")
```

## Rationale

- String concatenation creates separate translation units per fragment. Translators cannot reorder them for their language grammar.
- Named placeholders (`%(name)s` or `{name}`) give translators full context and freedom to reorder.
- `f-strings` are evaluated before `_()` is called, so the full string with values is sent to `_()`, never matching any `.po` entry.
- Use `_()` for user-facing strings only. Technical/debug strings do not need translation.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/i18n.html#translate-python-code
