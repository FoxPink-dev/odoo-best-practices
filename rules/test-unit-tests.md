---
priority: MUST
tags: [testing, unit-tests, python]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing unit tests"
    includes: ["tests/test_*.py", "tests/__init__.py"]
---
# Test Unit Tests

## Description

Odoo tests use Python's `unittest` library. All test modules must go in a `tests/` sub-package, be imported from `tests/__init__.py`, and have filenames starting with `test_`. Use `TransactionCase` (run each method in a savepoint sub-transaction) or `SingleTransactionCase` (all methods in one transaction). Never use plain `unittest.TestCase` without adding proper tags.

## Correct

```python
# tests/__init__.py
from . import test_partner, test_product

# tests/test_partner.py
from odoo.tests import TransactionCase

class TestPartner(TransactionCase):
    def test_compute_name(self):
        partner = self.env['res.partner'].create({'name': 'Test'})
        partner._compute_display_name()
        self.assertEqual(partner.display_name, 'Test')
```

## Incorrect

```python
# tests/test_stuff.py (not imported in __init__.py)
import unittest

class BadTest(unittest.TestCase):
    def test_something(self):
        # This won't be picked up by Odoo's test runner
        pass
```

## Rationale

Odoo's test runner auto-discovers only modules imported from `tests/__init__.py`. `TransactionCase` provides per-method transaction isolation (savepoints), `self.env`, `self.ref()`, and `self.browse_ref()` utilities. Plain `unittest.TestCase` lacks these and will not be run unless explicitly tagged with `@tagged('standard', 'at_install')`.

## References

- Odoo 17.0 Testing docs: "Testing Python code" section
- Odoo 17.0 Testing docs: `TransactionCase`, `SingleTransactionCase` class definitions
