---
priority: SHOULD
tags: [owl, structure, component]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "creating OWL components"
    includes: ["**/static/src/**/*.js"]
  - task: "structuring OWL modules"
    includes: ["**/static/src/**"]
---
# OWL Component File Structure (Three-File Pattern)

## Description

Each OWL component should be organized in three files: JavaScript logic, QWeb XML template, and SCSS styles. This separation follows Odoo's convention and enables clear compilation and debugging.

## Correct

```
my_addon/static/src/js/my_component.js       # Component class + logic
my_addon/static/src/xml/my_component.xml     # QWeb template  
my_addon/static/src/scss/my_component.scss   # Component styles
```

```javascript
// my_component.js
import { Component } from "@odoo/owl";
import { MyComponentTemplate } from "./my_component.xml";

export class MyComponent extends Component {
    static template = "my_addon.MyComponent";
}
```

## Incorrect

```
my_addon/static/src/my_component.js           # Everything in one file (no template/scss separation)
my_addon/static/src/my_addon_all.js           # All components in a single monolithic file
```

## Rationale

Odoo's asset system compiles JS, XML, and SCSS separately. Keeping them in separate files allows the build system to optimize each type independently and makes debugging easier (browser dev tools show the original file). Three-file pattern also follows modern frontend conventions (component-per-file).

## References

- Odoo 17.0 JavaScript reference: "Organizing OWL components"
- Odoo 18.0 OWL reference: Asset compilation pipeline
