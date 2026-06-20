---
priority: HIGH
tags: [migration, noupdate, data, xml-id]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "handling noupdate data in migration"
    includes: ["noupdate", "xml_id"]
  - task: "migrating XML data"
    includes: ["ir.model.data", "noupdate"]
---
# Migration noupdate Data Handling

## Description

Data marked as `noupdate="1"` in XML (sequences, email templates, scheduled actions) is not automatically updated during module upgrade. Migration scripts must explicitly handle these records by updating their XML IDs or values.

## Correct

```python
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Update noupdate record by XML ID
    template = env.ref("my_module.email_template_notification", raise_if_not_found=False)
    if template:
        template.write({
            "subject": "Updated Notification Subject",
            "body_html": "<p>New template body</p>",
        })
```

```xml
<!-- __manifest__.py — update existing noupdate record on upgrade -->
<record id="email_template_notification" model="mail.template" noupdate="1">
    <field name="subject">Updated Notification Subject</field>
    <field name="body_html"><![CDATA[<p>New template body</p>]]></field>
</record>
```

## Incorrect

```python
# WRONG: creating a duplicate instead of updating
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["mail.template"].create({...})  # Creates new template instead of updating
```

## Rationale

`noupdate="1"` records are inserted once during module installation and never updated on upgrade. If the XML definition changes in a new version, the database still has the old values. Migration scripts must explicitly update these records using `env.ref()` to find them by XML ID, or use `ir.model.data` to check if they exist. This is especially critical for email templates, sequences, and scheduled actions that users may have customized.

## References

- Odoo 17.0 Data docs: noupdate attribute
- Odoo 17.0 Migration docs: Handling noupdate records
- data-noupdate — noupdate best practices
