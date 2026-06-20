---
priority: MUST
tags: [owl, templates, naming]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating OWL templates"
    includes: ["**/static/**/xml/**"]
  - task: "naming QWeb templates"
    includes: ["templates.xml"]
---
# OWL Template Naming Conventions

## Description

OWL templates follow the `ModuleName.TemplateName` naming convention. Template IDs must be unique across the entire addon. Use a consistent prefix matching the module technical name to avoid collisions.

## Correct

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="o_my_module_component">
            <t t-esc="state.message"/>
        </div>
    </t>
    <t t-name="my_module.MyOtherComponent">
        <span><t t-esc="state.count"/></span>
    </t>
</templates>
```

## Incorrect

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="Component">               <!-- WRONG: no module prefix -->
        <div><t t-esc="state.message"/></div>
    </t>
    <t t-name="MyComp">                  <!-- WRONG: abbreviated, ambiguous -->
        <span><t t-esc="state.count"/></span>
    </t>
</templates>
```

## Rationale

QWeb template IDs are global. Without a module prefix, your template may conflict with another module's template of the same name. Odoo's own templates follow `ModuleName.TemplateName` (e.g., `web.Dialog`, `sale.OrderWidget`). The first letter of each segment is capitalized (PascalCase) for consistency with OWL component class names.

## References

- Odoo 17.0 JavaScript reference: OWL components — template naming
- Odoo 18.0 OWL reference: Asset declaration and template registration
