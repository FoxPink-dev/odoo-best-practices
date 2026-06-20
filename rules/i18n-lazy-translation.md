---
name: i18n-lazy-translation
priority: SHOULD
tags:
  - i18n
  - translation
  - lazy
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - define class attribute
  - define selection label
  - use string default
---
# i18n-lazy-translation — `_()`, `_lt()` Lazy Translation

Use `_()` for runtime translation and `_lt()` (lazy translate) for class-level and module-level strings that are evaluated before the language context is available.

## Correct

```python
from odoo import _, _lt

# Lazy translation for class-level attributes (evaluated at import time)
class MyModel(models.Model):
    _name = 'my.model'
    _description = _lt('My Model')

    state = fields.Selection([
        ('draft', _lt('Draft')),
        ('confirmed', _lt('Confirmed')),
    ], string=_lt('State'))

    def action_confirm(self):
        # Runtime translation (evaluated when method is called)
        message = _('Record %(name)s confirmed') % {'name': self.name}
        return {'type': 'ir.actions.act_window_close'}
```

## Incorrect

```python
from odoo import _

class MyModel(models.Model):
    _name = 'my.model'
    _description = _('My Model')  # Evaluated at import — wrong language may be active!

    state = fields.Selection([
        ('draft', _('Draft')),  # Evaluated at import time, not per-request
    ])
```

## Rationale

- `_()` evaluates translation immediately. Used at class level, it captures the language of the installation process, not the end user.
- `_lt()` (lazy translate) stores the string and evaluates `_()` lazily when the field is accessed, respecting the current user's language.
- Always use `_lt()` for: `_description`, `_rec_name`, `_sql_constraints` messages, `Selection` labels, default values, and any other class-level strings.
- Use `_()` only inside methods where a request context (and thus a language) is active.
- In QWeb templates, use `t-field` (auto-translates) or `t-esc` with translatable expressions.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/i18n.html#lazy-translation
