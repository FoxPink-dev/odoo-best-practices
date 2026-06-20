---
priority: MUST
tags: [testing, fixtures, setup, teardown]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing setUp or setUpClass in tests"
    includes: ["tests/test_*.py"]
---
# Test Fixtures

## Description

Use `setUpClass` for expensive, shared setup (runs once per test class). Use `setUp` only when each test method needs isolated fixtures. In `TransactionCase`, each test method runs in a savepoint that is rolled back after the test, so `setUpClass` is preferred for data that does not change between tests. Avoid `tearDown` unless you have side effects beyond the transaction (e.g., file cleanup, external service calls).

## Correct

```python
from odoo.tests import TransactionCase

class TestProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
        })

    def test_price(self):
        self.product.list_price = 100
        self.assertEqual(self.product.list_price, 100)

    def test_partner_email(self):
        self.partner.email = 'test@example.com'
        self.assertEqual(self.partner.email, 'test@example.com')
```

## Incorrect

```python
class BadTestProduct(TransactionCase):
    def setUp(self):
        super().setUp()
        # Runs before EVERY test - slow for large data
        self.partner = self.env['res.partner'].create({'name': 'Test'})
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
        })
```

## Rationale

`setUpClass` runs once per class, significantly reducing test suite time when setup is expensive (e.g., creating complex records). `TransactionCase` already rolls back per test, so shared data from `setUpClass` is automatically restored. Use `setUp` only when each test needs a unique/clean state that would be corrupted if shared.

## References

- Odoo 17.0 Testing docs: `TransactionCase` documentation
- Python unittest docs: `setUpClass`, `setUp`, `tearDown`
