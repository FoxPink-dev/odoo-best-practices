---
priority: SHOULD
tags: [coding-style, comments, docstrings]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "writing comments or docstrings"
    includes: ["*.py"]
---
# Code Comments

## Description

Write docstrings for all model classes (`_description` attribute) and public methods (triple-quoted description). Inline comments explain *why* not *what* (the code shows *what*). Use `#` for comments, `"""` for docstrings. Model `_description` is required and should be a short, human-readable name for the model.

## Correct

```python
class ResPartner(models.Model):
    _name = 'res.partner'
    _description = 'Partner'

    def action_confirm(self):
        """Confirm the partner's account after email verification."""
        # We check the email first because unverified emails can't be confirmed
        if not self.email:
            raise UserError(_("Cannot confirm a partner without email."))
        self.write({'state': 'confirmed'})
```

## Incorrect

```python
class ResPartner(models.Model):
    _name = 'res.partner'
    _description = 'Partner'  # Missing

    # This method confirms the partner
    def action_confirm(self):
        # Set state to confirmed
        self.state = 'confirmed'
        # Set date
        self.confirm_date = fields.Datetime.now()
```

## Rationale

Docstrings explain purpose and contract (what), while comments explain reasoning (why). The `_description` is used in Odoo UI for translatable model labels. Over-commenting obvious code (`# Set state to confirmed`) adds noise. Focus comments on non-obvious decisions, workarounds, or business rules.

## References

- PEP257 – Docstring Conventions
- Odoo coding guidelines: `_description` attribute required on models
