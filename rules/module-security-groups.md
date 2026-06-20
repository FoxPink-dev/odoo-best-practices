---
priority: MUST
tags: [module, security, groups, categories]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "defining security groups"
    includes: ["**/security/*.xml"]
  - task: "creating user categories"
    includes: ["**/security/*.xml"]
---

# Module Security Groups

## Description

Security groups (`res.groups`) are the foundation of Odoo's access control. They must follow a consistent naming convention and be organized in a category tree for the user form's application selection.

## Correct

```xml
<odoo>
    <!-- Create module category -->
    <record id="module_category_my_module" model="ir.module.category">
        <field name="name">My Module</field>
        <field name="description">My custom module description</field>
        <field name="sequence">10</field>
    </record>

    <!-- Base user group -->
    <record id="group_my_module_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>

    <!-- Manager inherits from User -->
    <record id="group_my_module_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
    </record>

    <!-- Group-specific menu visibility -->
    <record id="menu_my_module" model="ir.ui.menu">
        <field name="name">My Module</field>
        <field name="groups_id" eval="[(4, ref('group_my_module_user'))]"/>
        <field name="sequence">10</field>
    </record>
</odoo>
```

## Incorrect

```xml
<!-- WRONG: no module category - group appears in "Uncategorized" -->
<record id="group_my_module_user" model="res.groups">
    <field name="name">User</field>
    <!-- Missing category_id -->
</record>

<!-- WRONG: naming inconsistency -->
<record id="my_group_id" model="res.groups">
    <field name="name">My Module User</field>
</record>
```

## Rationale

- **Category tree**: Every module must create its own `ir.module.category` and assign all its groups to it. This makes groups appear as a single application section in the user form.
- **Naming convention**: XML IDs use the prefix `group_<module>_<role>`. Group names are short role descriptions (e.g., "User", "Manager", "Admin").
- **Inheritance via `implied_ids`**: Manager groups should imply (inherit from) User groups. This ensures managers get all user permissions plus extras.
- **Category hierarchy**: Use `/` separator in `ir.module.category.name` for nested categories (e.g., "Sales / My Module").
- **Menu/action visibility**: The `groups_id` attribute restricts visibility. Use group references to show/hide specific UI elements per role.

## References

- Odoo 17.0 Security: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html
