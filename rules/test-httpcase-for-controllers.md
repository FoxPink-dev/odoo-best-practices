---
name: test-httpcase-for-controllers
priority: medium
tags:
  - testing
  - httpcase
  - controller
  - api
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - test controller
  - test api endpoint
  - test tour
---

# test-httpcase-for-controllers — Use HttpCase for HTTP Tests

`HttpCase` spawns a real HTTP server, commits data to the database, and allows testing controllers, JSON endpoints, and JS tours end-to-end.

## Incorrect

```python
from odoo.tests import TransactionCase

class TestController(TransactionCase):
    # TransactionCase rolls back — HTTP server can't read uncommitted data
    def test_partner_create(self):
        # Can't make real HTTP requests here
        pass
```

## Correct

```python
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestPartnerAPI(HttpCase):

    def test_create_partner(self):
        self.authenticate('admin', 'admin')
        response = self.url_open(
            '/api/partner/create',
            data={'name': 'Test Partner', 'email': 'test@example.com'},
            headers={'Content-Type': 'application/json'},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('id', data)

    def test_search_endpoint(self):
        self.authenticate('admin', 'admin')
        response = self.url_open('/api/partner/search?name=Test')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
```

## Important: Data Pollution

`HttpCase` **commits** data to the database (unlike `TransactionCase`).

```python
@tagged('post_install', '-at_install')
class TestTour(HttpCase):

    def test_tour_flow(self):
        self.authenticate('admin', 'admin')
        # Use unique names to avoid collisions between test runs
        unique_name = f"Test Customer {datetime.now().timestamp()}"
        response = self.url_open('/api/customer/create', ...)

    def tearDown(self):
        # Explicitly clean up created records
        partner = self.env['res.partner'].search([('name', '=like', 'Test Customer%')])
        if partner:
            partner.unlink()
        super().tearDown()
```

## Methods

| Method | Purpose |
|--------|---------|
| `self.url_open(path, data=None, ...)` | HTTP request to the test server |
| `self.authenticate(user, password)` | Login as user |
| `self.browser_js(path, code, ...)` | Run JS tour in headless browser |
| `self.session` | Current session (dict) |

## When to Use What

| Test Type | Class | Reason |
|-----------|-------|--------|
| Business logic | TransactionCase | Fast, isolated, rolled back |
| Controller / API | HttpCase | Needs real HTTP server |
| JS tours | HttpCase | Needs browser + HTTP |
| Multi-step workflow | TransactionCase | Use setUpClass for shared data |

## Why

- `TransactionCase` doesn't commit — HTTP server can't see test data
- `HttpCase` provides `url_open()` and `browser_js()` for real HTTP testing
- Always tag with `post_install` - tests need all modules installed

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html
