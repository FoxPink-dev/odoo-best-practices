---
priority: MUST
tags: [owl, lifecycle, cleanup, subscriptions]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "subscribing to services in OWL"
    includes: ["onMounted", "onWillUnmount", "useService", "on"]
  - task: "cleaning up OWL effects"
    includes: ["addListener", "setInterval", "setTimeout"]
---
# OWL Cleanup Subscriptions

## Description

Always clean up subscriptions, event listeners, and timers when an OWL component is destroyed. Use the cleanup function returned by `onMounted`, `onWillUnmount`, or `onWillDestroy` hooks. Failing to clean up causes memory leaks and stale callbacks.

## Correct

```javascript
import { Component, onMounted, onWillUnmount } from "@odoo/owl";

export class LiveData extends Component {
    static template = "my_addon.LiveData";

    setup() {
        this._interval = null;
        onMounted(() => {
            this._interval = setInterval(() => this.refresh(), 5000);
        });
        onWillUnmount(() => {
            if (this._interval) {
                clearInterval(this._interval);
            }
        });
    }

    refresh() { /* ... */ }
}
```

## Incorrect

```javascript
import { Component, onMounted } from "@odoo/owl";

export class LiveData extends Component {
    static template = "my_addon.LiveData";

    setup() {
        onMounted(() => {
            setInterval(() => this.refresh(), 5000);   // WRONG: never cleared
        });
    }

    refresh() { /* ... */ }
}
```

## Rationale

OWL components are destroyed and recreated during normal navigation (e.g., switching views). Each `setInterval`, `addListener`, or `on` call without cleanup accumulates. After enough navigations, stale callbacks will execute on destroyed components, causing errors and performance degradation. Always pair subscriptions with cleanup in `onWillUnmount` or use the cleanup return value of `onMounted`.

## References

- OWL documentation: Lifecycle hooks — `onMounted`, `onWillUnmount`, `onWillDestroy`
- OWL documentation: useService — automatic cleanup
