---
name: write-inside-compute
severity: high
tags:
  - anti-pattern
  - orm
  - computed-fields
---

# write() Inside a Computed Field

## ❌ Anti-Pattern

```python
@api.depends('state')
def _compute_approval(self):
    for record in self:
        if record.state == 'approved':
            record.write({'approved_by': self.env.user.id})
```

## ✅ Fix

```python
@api.depends('state')
def _compute_approval(self):
    for record in self:
        record.approved_by = self.env.user.id if record.state == 'approved' else False
```

## Why It Hurts

`write()` triggers recomputation of all computed fields that depend on the written field. Inside a compute method, this causes a **recursive recomputation storm** — the field being computed triggers itself again.

## Detected When

- `self.write(...)`, `self.env[...].write(...)` inside a method decorated with `@api.depends`
- `self.create(...)` inside compute

## Rule

Computed fields should only set their own value: `record.field = value`. Never call `write()`, `create()`, or `unlink()` inside `@api.depends` methods.

## References

- perf-computed-dependencies
