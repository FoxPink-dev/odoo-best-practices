# Contributing to Odoo Best Practices

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/odoo-best-practices.git`
3. Create a branch: `git checkout -b feature/your-feature`

## Development Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

## Testing

```bash
# Run all tests
python -m pytest

# Run specific test
python -m pytest tests/test_checker.py
```

## Before Submitting

- [ ] Tests pass (`python -m pytest`)
- [ ] No lint errors (`ruff check .`)
- [ ] Run analyzer on a real Odoo addon: `python -m analyzer.cli path/to/addon --check`
- [ ] Update CHANGELOG.md

## Code Conventions

- Python 3.6+ (f-strings, type hints where helpful)
- Follow existing patterns (see `analyzer/checker.py`, `analyzer/store.py`)
- No comments in code unless explaining _why_ (not _what_)
- Async everywhere where applicable

## Adding a Rule

1. Add rule file in `rules/<rule-name>.md`
2. Implement check in `analyzer/checker.py`
3. Add anti-pattern doc in `bad_patterns/<rule-name>.md`
4. Add test in `tests/`

## Questions

Open a [Discussion](https://github.com/your-org/odoo-best-practices/discussions) or [Issue](https://github.com/your-org/odoo-best-practices/issues).
