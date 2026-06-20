---
name: lint-pre-commit
priority: low
tags:
  - lint
  - pre-commit
  - ci
odoo_versions:
  - 16
  - 17
  - 18
  - 19
triggers:
  - setup project
  - lint code
  - ci pipeline
---

# lint-pre-commit — Set Up Pre-commit Hooks

Every Odoo project should use pre-commit hooks with `pylint-odoo` and `flake8` to catch issues before code review.

## Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/OCA/pylint-odoo
    rev: v10.0.2
    hooks:
      - id: pylint_odoo
        name: pylint odoo
        args:
          - --valid-odoo-versions=19.0

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
        args: [--line-length=88]
```

## Installation

```bash
pip install pre-commit pylint-odoo flake8
pre-commit install
pre-commit run --all-files
```

## pylint-odoo Checks

| Check ID | What It Detects |
|----------|-----------------|
| `odoo-addons-relative-import` | Absolute import instead of relative |
| `odoo-exception-warning` | Warning instead of `raise` |
| `translation-*` | Translation method errors |
| `api-one-deprecated` | Using deprecated `@api.one` |
| `api-one-multi-deprecated` | Using deprecated `@api.multi` |
| `method-required-super` | Missing `super()` call |

## Recommended .pylintrc

```ini
[MASTER]
load-plugins=pylint_odoo
valid-odoo-versions=19.0

[MESSAGES CONTROL]
disable=all
enable=odoolint

[ODOOLINT]
readme_template_url=False
```

## Why

- Catches Odoo-specific issues that generic linters miss
- Enforces consistent code style across the team
- Runs automatically on every commit — no manual review overhead
- OCA requires it for all community contributions

## References

- https://github.com/OCA/pylint-odoo
- https://pre-commit.com
