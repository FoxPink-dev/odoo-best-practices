---
name: nocheck-in-constrains
severity: medium
tags:
  - anti-pattern
  - orm
  - validation
---

# Skipping Validation with `_nocheck`

## ❌ Anti-Pattern

```python
@api.constrains('date_start', 'date_end')
def _check_dates(self):
    for record in self:
        if record.date_end < record.date_start:
            raise ValidationError(_("End date must be after start date"))

# Somewhere else:
record._nocheck = True
record.date_end = record.date_start - timedelta(days=1)
```

## ✅ Fix

```python
# Proper state management instead of bypassing validation
record.write({'date_end': record.date_start + timedelta(days=1)})
```

## Why It Hurts

`_nocheck` silently skips ALL `@api.constrains` validation. This can lead to data integrity violations that cascade into accounting mismatches, inventory errors, and unrecoverable data corruption.

## Worst Offenders

- Skipping date validation → broken order pipelines
- Skipping uniqueness constraints → duplicate references
- Skipping financial validation → accounting imbalances

## Detected When

- `_nocheck = True` assigned anywhere in business code
- Used in migration scripts as a shortcut instead of proper data transformation

## References

- lint-api-decorators
