---
priority: SHOULD
tags: [orm, binary, attachment, fields]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining binary fields"
    includes: ["fields.Binary", "fields.Image"]
  - task: "handling file uploads"
    includes: ["Binary", "attachment"]
---
# ORM Binary Fields

## Description

Binary fields default to `attachment=True`, which stores the file as an `ir.attachment` record instead of in the model's database table. This is the recommended default because it moves large binary data out of the model's main table (improving query performance), enables the attachment to be served directly by the web client, and allows the file to be shared across records. Use `attachment=False` only when the binary data must be in the model's table (e.g., for direct SQL access). Use `fields.Image` for images to get automatic resizing.

## Correct

```python
from odoo import models, fields

class ProductImage(models.Model):
    _name = 'product.image'
    _description = 'Product Image'

    # Binary with attachment=True (default) — stored in ir.attachment
    image_1920 = fields.Image(string="Image", max_width=1920, max_height=1920)

    # Binary file with attachment=True
    datasheet = fields.Binary(string="Datasheet PDF")

    # Image with automatic resizing
    image_128 = fields.Image(string="Small Image", max_width=128, max_height=128)

    # Rare case: binary stored in model table
    checksum = fields.Binary(string="Checksum", attachment=False)
```

## Incorrect

```python
from odoo import models, fields

class ProductImage(models.Model):
    _name = 'product.image'

    # WRONG: attachment=False for an image — bloats the model's table
    image = fields.Binary(string="Image", attachment=False)

    # WRONG: using Binary for images — no automatic resizing
    image = fields.Binary(string="Image")
```

## Rationale

The Odoo 17.0 ORM documentation specifies for Binary fields: `attachment` parameter — "whether the field should be stored as ir_attachment or in a column of the model's table (default: True)." Storing as `ir.attachment` has significant advantages: the file is served via `/web/content` route, it participates in the attachment garbage collection, and it doesn't increase the row width of the model's main table. For images, `fields.Image` extends `Binary` with `max_width`, `max_height`, and `verify_resolution` parameters, automatically resizing images that exceed the limits while preserving aspect ratio.

## References

- Odoo 17.0 ORM docs: `fields.Binary` — attachment parameter defaults to True
- Odoo 17.0 ORM docs: `fields.Image` — extends Binary with max_width/max_height/verify_resolution
- Odoo 17.0 ORM docs: Attachment storage in ir.attachment vs model table column
