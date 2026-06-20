---
priority: MUST
tags: [testing, tagging, test-selection]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "tagging test classes"
    includes: ["tests/test_*.py"]
---
# Test Tags

## Description

Use `@tagged()` to control when and whether tests run. All `BaseCase` subclasses default to `standard` and `at_install`. Remove `standard` with `-standard` to exclude from default runs. Add `post_install` (with `-at_install`) for cross-module or HttpCase tests. Tag slow tests with a custom tag like `slow` so they can be excluded from quick CI runs.

## Correct

```python
from odoo.tests import TransactionCase, HttpCase, tagged

# Runs at install time (default)
class TestFast(TransactionCase):
    def test_something(self):
        pass

# Runs after all modules installed
@tagged('-at_install', 'post_install')
class TestPostInstall(HttpCase):
    def test_cross_module(self):
        pass

# Excluded from default runs
@tagged('-standard', 'slow')
class TestSlow(TransactionCase):
    def test_heavy(self):
        pass
```

## Incorrect

```python
# HttpCase without post_install - runs at_install when
# other modules may not be loaded
class BadTag(HttpCase):
    def test_tour(self):
        self.start_tour("/web", "tour_name")
```

```bash
# CLI: run only fast standard tests
$ odoo-bin --test-tags 'standard,-slow'

# CLI: run specific module
$ odoo-bin --test-tags /sale

# CLI: run specific method
$ odoo-bin --test-tags .test_confirm_changes_state
```

## Rationale

Tags give fine-grained control over which tests run in different contexts (CI, local dev, full test suite). The `-` prefix removes tags, `+` adds them. `--test-tags` accepts module (`/module`), class (`:Class`), and method (`.method`) selectors. Without proper tagging, HttpCase tests may fail because their dependencies aren't installed yet.

## References

- Odoo 17.0 Testing docs: `tagged()` decorator, "Test selection" and "Special tags" sections
- Odoo 17.0 Testing docs: `--test-tags` CLI invocation
