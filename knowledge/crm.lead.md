---
name: knowledge-crm-lead
model: crm.lead
module: crm
priority: medium
---
# crm.lead — Sales Leads & Opportunities

## Purpose
Tracks sales leads (unqualified) and opportunities (qualified with probability). The pipeline from first contact to won/lost.

## Key Fields
- `name` — Subject / opportunity name
- `partner_id` — Many2one to `res.partner` (customer)
- `contact_name` — Contact person (if partner not set)
- `email_from` — Email
- `phone` — Phone number
- `expected_revenue` — Monetary (expected amount)
- `probability` — Float 0-100 (won %)
- `planned_revenue` — Monetary (computed)
- `stage_id` — Many2one to `crm.stage` (pipeline stage)
- `team_id` — Many2one to `crm.team` (sales team)
- `user_id` — Many2one to `res.users` (salesperson)
- `date_open` — Date (first contacted)
- `date_deadline` — Date (expected close)
- `date_last_stage_update` — Datetime
- `type` — Selection: `lead` | `opportunity`
- `priority` — Selection: 0-3 (Do Not/Done/Low/High)
- `lost_reason_id` — Many2one to `crm.lost.reason`

## Common Methods
- `action_set_lost()` — Mark as lost with reason
- `action_set_won()` — Mark as won, create `sale.order`
- `_onchange_stage_id()` — Update probability on stage change
- `merge_opportunity()` — Merge duplicates
- `action_send_simple_email()` — Quick email composer

## Pipeline Automation

```python
# Automated stage transition
class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_set_won(self):
        res = super().action_set_won()
        # Post-automation: send welcome email
        return res
```

## Known Pitfalls
- `merge_opportunity()` is destructive — test thoroughly
- `expected_revenue` can be inflated by inconsistent probability
- Stage transitions trigger `_track_subtype()` for mail activity
- Don't hardcode `stage_id` — stages are configurable per team
