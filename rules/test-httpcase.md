---
priority: MUST
tags: [testing, httpcase, integration]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing HTTP or controller tests"
    includes: ["tests/test_*.py", "tests/*http*"]
---
# Test HttpCase

## Description

Use `HttpCase` for tests that need to verify controller responses, browser rendering, or tours. `HttpCase` extends `TransactionCase` with `url_open()` and `browser_js()` helpers that drive a headless Chrome instance. Tag HttpCase tests with `@tagged('-at_install', 'post_install')` so they run after all modules are installed.

## Correct

```python
from odoo.tests import HttpCase, tagged

@tagged('-at_install', 'post_install')
class TestWebsiteController(HttpCase):
    def test_page_loads(self):
        resp = self.url_open('/my/page')
        self.assertEqual(resp.status_code, 200)

    def test_tour(self):
        self.start_tour("/web", "my_module.my_tour", login="admin")
```

## Incorrect

```python
from odoo.tests import HttpCase

class BadHttpTest(HttpCase):
    def test_controller(self):
        # Missing post_install tag: this will run at_install
        # when other modules the test depends on may not be loaded
        resp = self.url_open('/some/page')
```

## Rationale

`HttpCase` tests depend on full web assets, frontend templates, and cross-module functionality. Running them `at_install` (the default) means dependent modules may not be present yet. Always use `post_install` for HttpCase tests. The `browser_js()` method provides Chrome headless automation; `start_tour()` is the preferred shorthand for launching tours.

## References

- Odoo 17.0 Testing docs: `HttpCase` class, `browser_js()`, `start_tour()`
- Odoo 17.0 Testing docs: "Special tags" section on `post_install`
