---
priority: SHOULD
tags: [testing, tours, integration, javascript]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing tour tests"
    includes: ["static/tests/tours/*.js", "tests/test_tour*.py"]
---
# Test Tour

## Description

Tours are integration tests that simulate real user scenarios in the browser. They verify Python and JavaScript components work together. Define tours in JS files under `static/tests/tours/`, register them with `web_tour.tour`, and trigger them from Python `HttpCase` tests using `start_tour()`.

## Correct

```javascript
// static/tests/tours/my_tour.js
/** @odoo-module **/
import tour from 'web_tour.tour';

tour.register('my_module.my_tour', {
    url: '/web',
    test: true,
}, [
    tour.stepUtils.showAppsMenuItem(),
    {
        trigger: '.o_app[data-menu-xmlid="my_module.menu_root"]',
        content: 'Open my module',
    },
    {
        trigger: 'button:contains("Create")',
        extra_trigger: '.o_list_view',
    },
]);
```

```python
# tests/test_tour.py
from odoo.tests import HttpCase, tagged

@tagged('-at_install', 'post_install')
class TestMyTour(HttpCase):
    def test_my_tour(self):
        self.start_tour("/web", "my_module.my_tour", login="admin")
```

## Incorrect

```python
# Missing post_install tag
class BadTourTest(HttpCase):
    def test_tour(self):
        self.start_tour("/web", "my_module.my_tour", login="admin")
```

## Rationale

Tours are the only way to test full-stack integration (Python server + JavaScript frontend). Registering with `test: true` marks the tour for automated testing only (hidden from the UI tour menu). The last step should leave the page in a stable state with no ongoing edits or pending network requests. Use `extra_trigger` to ensure modal/wizard context before interacting.

## References

- Odoo 17.0 Testing docs: "Integration Testing" / "Writing a test tour" section
- Odoo 17.0 Testing docs: `start_tour()`, `browser_js()` API
