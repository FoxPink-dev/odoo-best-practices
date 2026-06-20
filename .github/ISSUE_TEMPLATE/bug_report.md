---
name: Bug Report
about: Report a false positive, false negative, or crash
title: ''
labels: bug
assignees: ''
---

## Describe the Bug

A clear description of the issue.

## To Reproduce

```bash
python -m analyzer.cli path/to/addon --check
```

## Expected vs Actual

```
Expected: No violation for this pattern
Actual:   False positive: search-inside-loop on line 42
```

## Environment

- Odoo version: [14/15/16/17/18/19]
- Python version: [3.6+]
- OS: [Windows/macOS/Linux]

## Addon Sample

```python
# Minimal code snippet that triggers the bug
```

## Screenshots

If applicable.
