---
name: knowledge-project-task
model: project.task
module: project
priority: medium
---
# project.task — Project Tasks

## Purpose
Tracks individual work items within projects. Supports subtasks, dependencies, time tracking, and collaboration.

## Key Fields
- `name` — Task title
- `project_id` — Many2one to `project.project`
- `stage_id` — Many2one to `project.task.type`
- `parent_id` — Many2one to `project.task` (subtask relation)
- `child_ids` — One2many to `project.task`
- `user_ids` — Many2many to `res.users` (assignees)
- `partner_ids` — Many2many to `res.partner` (followers)
- `deadline` — Date
- `planned_hours` — Float
- `remaining_hours` — Float
- `effective_hours` — Float (computed from timesheets)
- `total_hours_spent` — Float (computed)
- `priority` — Selection: 0-3
- `kanban_state` — Selection: `normal` | `done` | `blocked`
- `allow_timesheets` — Boolean (from project config)
- `timesheet_ids` — One2many to `account.analytic.line`
- `description` — Html
- `sequence` — Integer (ordering)
- `tag_ids` — Many2many to `project.tags`
- `working_hours_closed` — Boolean (blocked beyond estimate)

## Task States
```
To Do → In Progress → Done
                        ↓
                     Cancelled
```

## Common Methods
- `action_open_task()` — Open task form
- `action_assign_to_me()` — Quick self-assign
- `_compute_effective_hours()` — Sum timesheets
- `action_see_timesheets()` — Open timesheet lines
- `_check_subtask_completion()` — Validate subtask dependencies

## Subtask Pattern

```python
class ProjectTask(models.Model):
    _inherit = "project.task"

    def action_create_subtask(self, name):
        """Create a subtask under current task"""
        return self.create({
            "parent_id": self.id,
            "project_id": self.project_id.id,
            "name": name,
        })
```

## Known Pitfalls
- Subtask recursion (limit to 1 level in most installs)
- `planned_hours` vs `effective_hours` — don't set both
- Task deletion deletes child tasks, timesheets
- Timesheet lines are `account.analytic.line` — linked to accounting
- `allow_timesheets` controlled by project, not task
