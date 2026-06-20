---
priority: SHOULD
tags: [testing, coverage, quality]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "determining test coverage scope"
    includes: ["tests/test_*.py"]
---
# Test Coverage

## Description

Focus tests on: (1) business logic methods (`action_confirm`, `action_done`, `_compute_*`), (2) constraint methods (`@api.constrains`), (3) edge cases and boundary values, (4) security access rules (multi-user scenarios), (5) workflow state transitions, and (6) fixed bugs (regression tests). Not every getter/setter needs a test; prioritize high-risk, high-complexity code. Aim to cover both happy paths and error paths.

## Correct

```python
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestOrder(TransactionCase):
    def test_confirm_changes_state(self):
        order = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Test'}).id,
        })
        order.action_confirm()
        self.assertEqual(order.state, 'sale')

    def test_confirm_no_stock_raises(self):
        product = self.env['product.product'].create({
            'name': 'Test',
            'type': 'product',
            'qty_available': 0,
        })
        order = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Test'}).id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 10,
            })],
        })
        with self.assertRaises(ValidationError):
            order.action_confirm()

    def test_regression_partner_name_unicode(self):
        # Regression test for a bug fixed in v17
        partner = self.env['res.partner'].create({'name': 'Café Münster'})
        self.assertEqual(partner.name, 'Café Münster')
```

## Incorrect

```python
class BadCoverage(TransactionCase):
    def test_create_partner(self):
        # Tests basic ORM create - low value
        partner = self.env['res.partner'].create({'name': 'Test'})
        self.assertTrue(partner)

    def test_read_name(self):
        # Tests a simple field read
        partner = self.env.ref('base.partner_admin')
        self.assertEqual(partner.name, 'Administrator')
```

## Rationale

The Odoo ORM is already well-tested by Odoo SA. Focus test effort on your custom business logic, constraints, workflows, and integration points. Regression tests for fixed bugs are especially valuable as they prevent re-introduction. A small, focused test suite that runs quickly is more maintainable than a large one with low-value tests.

## References

- Odoo 17.0 Testing docs: "Best Practices" section (no full coverage needed, smaller tests better)
- Odoo 17.0 Testing docs: `assertQueryCount()` for performance regression
