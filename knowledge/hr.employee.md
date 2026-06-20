---
name: knowledge-hr-employee
model: hr.employee
module: hr
priority: medium
---
# hr.employee — Employees

## Purpose
Represents company employees with HR data: contracts, attendance, leaves, skills, and personal info.

## Key Fields
- `name` — Employee name
- `user_id` — Many2one to `res.users` (linked user account)
- `department_id` — Many2one to `hr.department`
- `job_id` — Many2one to `hr.job`
- `parent_id` — Many2one to `hr.employee` (manager)
- `coach_id` — Many2one to `hr.employee` (coach/mentor)
- `contract_id` — Many2one to `hr.contract` (current contract)
- `resource_id` — Many2one to `resource.resource` (calendar/leave allocation)
- `work_contact_id` — Many2one to `res.partner` (work address)
- `address_home_id` — Many2one to `res.partner` (home address)
- `company_id` — Many2one to `res.company`
- `active` — Boolean
- `employee_type` — Selection: `employee` | `student` | `trainee` | `freelance`
- `identification_id` — Char (tax/ID number)
- `passport_id` — Char (passport)
- `gender` — Selection: `male` | `female` | `other`
- `birthday` — Date
- `km_home_work` — Float (commute distance)

## Leave Management
- `remaining_leaves` — Float (computed, days remaining)
- `leave_ids` — One2many to `hr.leave`
- `total_leave_days` — Float (computed)

## Common Methods
- `_compute_leave_count()` — Calculate leave balances
- `_get_contract()` — Get current contract
- `action_open_employee()` — Open employee form
- `action_see_contracts()` — Show contract history
- `action_see_leaves()` — Show leave history

## Contract Integration

```python
class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_next_contract(self, date=None):
        """Get next non-expired contract"""
```

## Known Pitfalls
- `user_id` can be empty (employee may not have login)
- Employee deletion cascade-deletes contracts, timesheets
- `resource_id` auto-created on employee creation
- `remaining_leaves` depends on allocation type (paid/unpaid)
