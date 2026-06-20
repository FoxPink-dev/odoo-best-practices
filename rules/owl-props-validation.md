---
priority: MUST
tags: [owl, props, validation, types]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining component props"
    includes: ["**/static/src/**/*.js"]
  - task: "passing props to OWL components"
    includes: ["**/*.xml"]
---
# OWL Props Validation

## Description

OWL components must define a `static props` descriptor that validates all received props. This catches bugs early and documents the component's public API. Use `PropTypes` from `@odoo/owl` for type checking.

## Correct

```javascript
import { Component } from "@odoo/owl";

export class SaleOrderLine extends Component {
    static props = {
        id: { type: Number },
        productName: { type: String },
        quantity: { type: Number, optional: true },
        onDelete: { type: Function, optional: true },
    };

    static template = "my_addon.SaleOrderLine";
}
```

## Incorrect

```javascript
import { Component } from "@odoo/owl";

export class SaleOrderLine extends Component {
    static template = "my_addon.SaleOrderLine";

    setup() {
        // WRONG: accessing props without validation
        console.log(this.props.productName);
    }
}
```

## Rationale

Without props validation, passing incorrect prop types silently fails or produces cryptic runtime errors. The props descriptor serves as self-documenting API contract. OWL's `PropTypes` validates at runtime in dev mode. In production, type mismatches may cause unpredictable behavior.

## References

- OWL documentation: Props — validation and typing
- Odoo 17.0 JavaScript reference: Component props descriptor
- OWL PropTypes: `Array`, `Boolean`, `Date`, `Function`, `Number`, `Object`, `String`, `Element`
