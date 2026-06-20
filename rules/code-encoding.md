---
priority: SHOULD
tags: [coding-style, encoding, unicode, python]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "handling strings, encoding, or unicode"
    includes: ["*.py", "*.xml"]
---
# Code Encoding

## Description

All Python files should use UTF-8 encoding (default in Python 3, no `# -*- coding: utf-8 -*-` needed in Odoo 17+ but still commonly used for 14-16 compatibility). Use `str` (Python 3 native Unicode) for all text. Use `fields.Text` translated for user-facing content. Use `safe_eval` instead of `eval()` for evaluating expressions. Use `odoo.tools.ustr()` for safe string conversion when needed.

## Correct

```python
from odoo import _, fields, models
from odoo.tools import ustr, safe_eval

class ResPartner(models.Model):
    _name = 'res.partner'

    notes = fields.Text(string='Notes', translate=True)  # User-facing, translatable

    name = fields.Char(string='Name', translate=True)

    def process_notes(self):
        # Safe string handling
        input_text = ustr(self.notes)
        # safe_eval instead of eval
        result = safe_eval(input_text, {'self': self})
        return result

    def _build_display_name(self):
        names = []
        if self.company_name:
            names.append(self.company_name)
        if self.name:
            names.append(self.name)
        return " - ".join(names)  # Unicode-safe string joining
```

## Incorrect

```python
# Not needed in Python 3, but harmless
# -*- coding: utf-8 -*-

# eval() is dangerous
def parse_expression(self, expr):
    return eval(expr)  # Security risk

# Using bytes for text
def get_name(self):
    return bytes(self.name, 'utf-8')  # Should return str
```

## Rationale

Python 3 uses `str` = Unicode natively; no manual encoding/decoding is needed for normal operations. `translate=True` enables per-language field values via `ir.translation`. Never use `eval()` with untrusted input (security). `safe_eval` restricts available functions and namespaces. XML files should declare `utf-8` encoding in the XML declaration.

## References

- Python 3 Unicode HOWTO
- Odoo ORM docs: `translate` attribute on fields
- Odoo security: `safe_eval` vs `eval`
