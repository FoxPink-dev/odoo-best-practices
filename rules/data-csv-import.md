---
name: data-csv-import
priority: MUST
tags:
  - data
  - csv
  - import
odoo_versions:
  - 14.0
  - 15.0
  - 16.0
  - 17.0
  - 18.0
  - 19.0
  - master
triggers:
  - create csv file
  - import data
  - define access csv
---
# data-csv-import — CSV Data File Best Practices

CSV files are used for model data that is tabular and stable, most commonly `ir.model.access.csv` for ACLs. Follow strict formatting rules.

## Correct

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

```csv
id,res_id,report_type,binding_model_id,report_name,paperformat_id:id
action_report_delivery_slip,delivery_slip,qweb-pdf,stock.picking,Stock Picking,
```

## Incorrect

```csv
# Missing header row (Odoo will fail)
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0

# Extra whitespace in values
id , name , model_id:id , group_id:id , perm_read
access_my_model_user , my.model , model_my_model , base.group_user , 1

# Using commas inside values without quoting
id,name,description
my_record,My Record,This has a, comma inside
```

## Rationale

- The first row **must** be a header with exact Odoo field names.
- Column order is irrelevant — Odoo matches by header name.
- Relational fields use the `field_id:id` notation to reference XML IDs.
- Whitespace in headers or values causes silent parse errors.
- CSV is only appropriate for simple, non-nested, non-relational data. For complex data with `<field>` tags, use XML.

## References
- https://www.odoo.com/documentation/18.0/developer/reference/backend/data.html#csv-files
- https://www.odoo.com/documentation/18.0/developer/reference/backend/security.html#access-rights
