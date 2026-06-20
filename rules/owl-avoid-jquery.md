---
priority: SHOULD
tags: [owl, jquery, dom, anti-pattern]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "using jQuery in OWL components"
    includes: ["**/static/src/**/*.js"]
  - task: "DOM manipulation"
    includes: ["$(", "jQuery", "document.querySelector"]
---
# Avoid jQuery in OWL Components

## Description

Never use jQuery (`$()`) for DOM manipulation inside OWL components. jQuery bypasses OWL's virtual DOM reconciliation, causing state/UI desynchronization, memory leaks, and hard-to-debug bugs. Use OWL refs and native DOM APIs instead.

## Correct

```javascript
import { Component, useRef, onMounted } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "my_addon.MyComponent";

    setup() {
        this.inputRef = useRef("myInput");
        onMounted(() => {
            this.inputRef.el.focus();
        });
    }
}
```

## Incorrect

```javascript
import { Component, onMounted } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "my_addon.MyComponent";

    setup() {
        onMounted(() => {
            // WRONG: jQuery bypasses OWL's VDOM
            $(this.el).find(".my-input").focus();

            // WRONG: direct DOM mutation
            this.el.querySelector(".my-input").value = "test";

            // WRONG: jQuery plugins modify DOM outside OWL
            $(this.el).datepicker();
        });
    }
}
```

## Rationale

OWL uses a virtual DOM diffing algorithm. Direct DOM manipulation via jQuery or native APIs happens outside this system — OWL cannot detect these changes and may overwrite them on the next render. Additionally, jQuery event listeners attached directly to DOM elements are not cleaned up when OWL destroys the component, causing memory leaks. Use `useRef` for DOM references and `useEffect`/`onMounted` for controlled side effects.

## References

- OWL documentation: Refs — `useRef`
- Odoo 17.0 JavaScript migration: Removing jQuery dependencies
- OWL rendering cycle: virtual DOM vs direct manipulation
