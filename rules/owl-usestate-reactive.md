---
priority: MUST
tags: [owl, state, reactive, usestate]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "managing component state"
    includes: ["**/static/src/**/*.js"]
  - task: "using useState"
    includes: ["useState"]
---
# OWL useState for Reactive State

## Description

Use `useState()` to make component state reactive. State objects wrapped with `useState()` trigger automatic re-renders when properties change. Never mutate state directly without `useState`.

## Correct

```javascript
import { Component, useState } from "@odoo/owl";

export class Counter extends Component {
    static template = "my_addon.Counter";

    setup() {
        this.state = useState({
            count: 0,
            label: "Counter",
        });
    }

    increment() {
        this.state.count++;
    }
}
```

## Incorrect

```javascript
import { Component } from "@odoo/owl";

export class Counter extends Component {
    static template = "my_addon.Counter";

    setup() {
        this.count = 0;     // WRONG: not reactive, changes won't re-render
        this.state = {       // WRONG: plain object, not wrapped in useState
            count: 0,
        };
    }

    increment() {
        this.count++;                       // No re-render
        this.state.count++;                 // No re-render either
    }
}
```

## Rationale

OWL components only re-render when their reactive state (tracked by `useState`) changes. Plain object properties are not observed. `useState` returns a Proxy that intercepts property changes and schedules a render. Always wrap component state that affects the UI in `useState`. Use plain properties only for non-reactive data.

## References

- OWL documentation: useState hook
- OWL Reactivity model: Proxy-based observation
- OWL rendering cycle: when and how components re-render
