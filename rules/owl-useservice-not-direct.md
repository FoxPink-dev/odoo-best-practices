---
name: owl-useservice-not-direct
priority: low-medium
tags:
  - owl
  - services
  - dependency-injection
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - call orm from js
  - show notification
  - use rpc
---

# owl-useservice-not-direct — Use useService for Odoo Services

Never import or instantiate Odoo services directly. Use the `useService()` hook which provides proper dependency injection and testability.

## Incorrect

```javascript
import { orm } from "@web/core/orm_service";

class PartnerList extends Component {
    setup() {
        // BAD: direct import — breaks DI, hard to test
        this.partners = await orm.searchRead(...);
    }
}
```

## Correct

```javascript
const { Component, useState, onWillStart } = owl;
const { useService } = require("@web/core/utils/hooks");

class PartnerList extends Component {
    static template = "my_module.PartnerList";

    setup() {
        this.state = useState({ partners: [] });
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.router = useService("router");

        onWillStart(async () => {
            this.state.partners = await this.orm.searchRead(
                "res.partner",
                [],
                ["id", "name", "email"]
            );
        });
    }

    async deletePartner(partnerId) {
        try {
            await this.orm.unlink("res.partner", [partnerId]);
            this.notification.add("Partner deleted", { type: "success" });
            await this._reloadData();
        } catch (error) {
            this.dialog.add("Error", "Failed to delete partner");
        }
    }
}
```

## Available Services

| Service Name | Purpose |
|-------------|---------|
| `"orm"` | ORM calls: searchRead, create, write, unlink |
| `"notification"` | Show toast notifications |
| `"dialog"` | Open dialog/modal windows |
| `"router"` | Navigate between views |
| `"rpc"` | Custom RPC calls |
| `"user"` | Current user info |
| `"action"` | Execute server actions |
| `"menu"` | Menu navigation |
| `"hotkey"` | Keyboard shortcuts |

## Why

- Services are singletons managed by Odoo's DI container
- Direct imports bypass dependency injection — can't be mocked in tests
- `useService()` is the official OWL pattern for accessing Odoo infrastructure
- Services provide consistent error handling and integration with the web client

## References

- https://www.odoo.com/documentation/19.0/developer/reference/frontend/owl_components.html
