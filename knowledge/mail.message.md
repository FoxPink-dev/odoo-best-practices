---
name: knowledge-mail-message
model: mail.message
module: mail
priority: medium
---
# mail.message — Messages & Notifications

## Purpose
Core communication model: internal notes, email messages, notifications, and chatter activity log.

## Key Fields
- `subject` — Char (message subject)
- `body` — Html (message content)
- `author_id` — Many2one to `res.partner`
- `model` — Char (related document model)
- `res_id` — Integer (related document ID)
- `record_name` — Char (display name of related doc)
- `message_type` — Selection: `email` | `comment` | `notification` | `user_notification`
- `subtype_id` — Many2one to `mail.message.subtype` (visibility/classification)
- `parent_id` — Many2one to `mail.message` (thread parent)
- `partner_ids` — Many2many to `res.partner` (recipients)
- `channel_ids` — Many2many to `mail.channel`
- `attachment_ids` — Many2many to `ir.attachment`
- `starred` — Boolean (pinned)
- `date` — Datetime
- `is_internal` — Boolean (internal only)
- `needaction_partner_ids` — Many2many (pending action)
- `notified_partner_ids` — Many2many (already notified)
- `no_auto_thread` — Boolean (skip auto-thread linking)

## Message Creation

```python
# Post a message on any record
record.message_post(
    body="<p>Message content</p>",
    subject="Optional subject",
    message_type="comment",
    subtype_xmlid="mail.mt_comment",
    partner_ids=[partner.id],
)
```

## Subtypes
- `mail.mt_comment` — Visible to everyone
- `mail.mt_note` — Internal note
- `mail.mt_activities` — Activity tracking
- Custom subtypes defined in `mail.message.subtype` model

## Notification System
- `needaction_partner_ids` — Partners required to act
- `notified_partner_ids` — Partners already notified
- Notifications are pushed via bus or email

## Common Methods
- `message_post()` — Post message on document
- `message_subscribe()` — Add followers
- `message_unsubscribe()` — Remove followers
- `message_format()` — Format for client
- `_notify()` — Internal notification dispatch
- `_message_read()` — Mark as read

## Known Pitfalls
- Large `body` values cause chatter performance issues
- `message_post()` triggers `_track_subtype()` — test tracking in overrides
- Don't bypass `message_post()` with direct create — breaks notifications
- `author_id` defaults to current user's partner — override explicitly
