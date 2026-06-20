---
name: i18n-translation-files
priority: MUST
tags:
  - i18n
  - translation
  - po
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - add translation
  - create po file
---
# i18n-translation-files — .po File Management

Translation files follow the GNU gettext `.po` format. Odoo uses the `i18n/` directory for module-level translations and `i18n_extra/` for additional community translations.

## Correct

```
my_module/
├── i18n/
│   ├── fr.po               # French translation
│   ├── de.po               # German translation
│   ├── es.po               # Spanish translation
│   ├── ja.po               # Japanese translation
│   └── fr_BE.po            # French (Belgium) regional variant
├── i18n_extra/
│   └── fr.po               # Additional non-module strings
```

```po
#. module: my_module
#. openerp-web
#: model:ir.model.fields,field_description:my_module.field_my_model__name
msgid "Name"
msgstr "Nom"

#. module: my_module
#: model:ir.ui.view,arch_db:my_module.view_my_model_form
msgid "Save & Close"
msgstr "Enregistrer et fermer"
```

## Incorrect

```po
# Missing module metadata
msgid "Name"
msgstr "Nom"

# Unescaped special characters
msgid "Product's price"
msgstr "Prix du produit"
```

## Rationale

- Always include the `#. module:` comment so Odoo knows which module owns the string.
- Use `msgid` for the English source string exactly as it appears in the code.
- Use `msgstr` for the translated string. Leave empty if untranslated.
- For plural forms, use `msgid_plural` and `msgstr[0]`, `msgstr[1]`.
- Generate `.pot` template files with `odoo-bin genpo --module my_module`.
- Never edit `.pot` files directly — they are templates regenerated from source.
- Regional variants (`fr_BE`, `pt_BR`) fall back to the base language (`fr`, `pt`).

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/i18n.html
- https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html
