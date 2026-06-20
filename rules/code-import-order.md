---
priority: MUST
tags: [coding-style, imports, python]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "organizing imports in Python files"
    includes: ["*.py"]
---
# Code Import Order

## Description

Group imports in this order, separated by a blank line: (1) standard library, (2) third-party libraries (including `odoo`), (3) Odoo addon imports (`from odoo.addons...`). Within each group, sort alphabetically. Use explicit imports: import specific classes/functions, not modules. Never use wildcard imports.

## Correct

```python
# 1. Standard library
import json
import logging
from datetime import datetime

# 2. Odoo imports
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, format_date

# 3. Other addons
from odoo.addons.base.models.res_bank import ResBank

_logger = logging.getLogger(__name__)
```

## Incorrect

```python
# Wrong: no grouping, not alphabetically sorted
from odoo.addons.sale.models.sale_order import SaleOrder
import json
from odoo import models, fields
import logging
from datetime import datetime
```

## Rationale

Standardized import order improves readability and prevents merge conflicts. Alphabetical sorting makes it easy to find imports. Explicit imports (importing classes/functions) makes dependencies clear and avoids namespace pollution. The `_logger` convention (`logging.getLogger(__name__)`) is Odoo-standard and should follow imports.

## References

- PEP8 import ordering guidelines
- Odoo coding guidelines: Import conventions
