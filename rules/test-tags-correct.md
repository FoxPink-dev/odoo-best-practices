---
name: test-tags-correct
priority: medium
tags:
  - testing
  - tags
  - ci
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - tag test
  - ci pipeline
  - test discovery
---

# test-tags-correct — Use Correct Test Tags

Tags control when and how tests execute. Wrong tags cause tests to run at the wrong time, producing false failures or being silently skipped.

## Incorrect

```python
from odoo.tests import TransactionCase

class TestSaleOrder(TransactionCase):
    # Uses default tags: 'standard', 'at_install'
    # Runs during module installation — before account is installed
    # → Fails if test depends on account module

    def test_discount(self):
        # requires account.tax data → fails randomly
        ...
```

## Correct

```python
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestSaleDiscount(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # account, stock, etc. are all installed now
        cls.tax = cls.env['account.tax'].create(...)

    def test_discount_calculation(self):
        order = self.env['sale.order'].create(...)
        order.action_confirm()
        self.assertEqual(order.amount_tax, 100.0)

@tagged('standard', 'at_install')
class TestSaleCore(TransactionCase):
    # Pure unit tests — no cross-module deps
    # Safe to run at install time

    def test_order_state(self):
        order = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Test'}).id,
        })
        self.assertEqual(order.state, 'draft')
```

## Tag Reference

| Tag | Default | Behavior |
|-----|---------|----------|
| `standard` | Yes | Included in default test run |
| `at_install` | Yes | Runs during module installation |
| `post_install` | No | Runs after all modules are installed |
| `-at_install` | - | Negation — excludes from install-time |
| Custom (e.g. `slow`) | No | Filter via `--test-tags slow` |

## When to Use What

| Situation | Tags |
|-----------|------|
| Pure unit test, own module only | `standard`, `at_install` (default) |
| Cross-module test (sale + account) | `post_install`, `-at_install` |
| Slow integration test | `post_install`, `-at_install`, `slow` |
| HTTP/tour test | `post_install`, `-at_install` |

## Why

- `at_install` runs before other modules are installed → missing deps cause failures
- `post_install` defers tests until all modules are ready
- Without correct tags, tests pass locally but fail in CI
- `-at_install` prevents double execution (both at_install and post_install)

## References

- https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html
