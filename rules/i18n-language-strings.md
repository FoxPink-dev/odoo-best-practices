---
name: i18n-language-strings
priority: SHOULD
tags:
  - i18n
  - language
  - UI
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - define language selector
  - add UI language string
---
# i18n-language-strings — Language Selection UI Strings

Language-related user interface strings must be translatable and should use the language's native name for display.

## Correct

```xml
<!-- Language selection with native names -->
<record id="lang_fr" model="res.lang">
  <field name="name">Français</field>
  <field name="code">fr</field>
  <field name="url_code">fr</field>
  <field name="direction">ltr</field>
  <field name="date_format">%d/%m/%Y</field>
  <field name="time_format">%H:%M:%S</field>
  <field name="grouping">[3,0]</field>
</record>
```

```python
class ResLang(models.Model):
    _inherit = 'res.lang'

    def _get_languages(self):
        """Return languages with native display names."""
        return [(lang.code, lang.name) for lang in self.search([])]
```

## Incorrect

```xml
<!-- English label instead of native name -->
<record id="lang_fr" model="res.lang">
  <field name="name">French</field>
  <field name="code">fr</field>
</record>
```

```python
# Hardcoded language list
LANGUAGES = [
    ('en_US', 'English'),
    ('fr_FR', 'French'),
    ('de_DE', 'German'),
]
```

## Rationale

- A language's display name must be in its own language ("Français", not "French") so users can recognize their language in a dropdown.
- Avoid hardcoding language lists. Use `res.lang` data or the `_get_languages()` helper for dynamic language selection.
- When rendering language options in a custom widget, respect `res.lang`'s `active` flag to hide uninstalled languages.
- Language codes should follow the `language_TERRITORY` format (`en_US`, `fr_BE`, `pt_BR`).

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/i18n.html#languages
