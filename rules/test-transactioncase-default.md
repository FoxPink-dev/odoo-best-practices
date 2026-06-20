---
name: test-transactioncase-default
priority: medium
tags:
  - testing
  - transactioncase
  - unit-test
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - write test
  - add unit test
  - test business logic
---

# test-transactioncase-default — Use TransactionCase for Business Logic Tests

`TransactionCase` is the workhorse of Odoo testing. Each test method runs in its own transaction that automatically rolls back — no side effects between tests.

## Incorrect

```python
from unittest import TestCase

class TestMyModel(TestCase):
    # Plain unittest.TestCase — no DB rollback!
    # Data leaks between tests, polluting results
    def test_create_order(self):
        order = self.env['sale.order'].create(...)
```

## Correct

```python
from odoo.tests import TransactionCase, tagged

@tagged('standard', 'at_install')
class TestSaleOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Shared test data — created once per class
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
        })

    def test_order_total(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 100.0,
            })],
        })
        order.action_confirm()
        self.assertEqual(order.amount_total, 200.0)

    def test_order_state_on_create(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        self.assertEqual(order.state, 'draft')
```

## Test Class Comparison

| Class | Transaction Rollback | HTTP Server | Use Case |
|-------|---------------------|-------------|----------|
| `TransactionCase` | Per test method | No | Business logic, ORM operations |
| `SingleTransactionCase` | Per class | No | Tests needing shared state |
| `HttpCase` | No (commits) | Yes | Controllers, JS tours, HTTP |

## Why

- Each test is isolated — no data leaks between tests
- Tests run fast (no DB cleanup needed)
- CI-friendly: parallel execution is safe
- Odoo registry, env, and users are pre-configured

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html
