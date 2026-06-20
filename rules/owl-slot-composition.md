---
priority: SHOULD
tags: [owl, slots, composition, templates]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "using slots in OWL templates"
    includes: ["**/*.xml"]
  - task: "composing components"
    includes: ["**/static/src/**/*.xml"]
---
# OWL Slot Composition

## Description

Use OWL slots (`<t-slot>`, `<t-slot-fallback>`) to compose components. Slots allow parent components to inject arbitrary content into child components, enabling flexible and reusable component hierarchies.

## Correct

```xml
<!-- Card component template (card.xml) -->
<div class="o_card">
    <div class="o_card_header">
        <t t-slot="header"/>
    </div>
    <div class="o_card_body">
        <t t-slot="default"/>
    </div>
    <div class="o_card_footer">
        <t t-slot="footer">
            <span>Default footer</span>
        </t>
    </div>
</div>

<!-- Usage in parent -->
<t t-name="my_addon.ProductPage">
    <Card>
        <t t-set-slot="header">
            <h2>Product Details</h2>
        </t>
        <t t-set-slot="default">
            <p>Product description here...</p>
        </t>
    </Card>
</t>
```

## Incorrect

```xml
<!-- WRONG: hardcoding child content in the component -->
<div class="o_card">
    <h2>Product Details</h2>
    <p>Product description here...</p>
</div>

<!-- WRONG: using t-esc instead of composition -->
<div class="o_card">
    <t t-esc="props.body"/>
</div>
```

## Rationale

Slots enable the component composition pattern, which is more flexible than inheritance for UI components. The parent decides what content goes where, while the child defines the layout structure. `t-slot-fallback` provides default content when the parent doesn't set a slot. Named slots (header, footer, default) allow multiple injection points.

## References

- OWL documentation: Slots — `<t-slot>`, `<t-set-slot>`, `<t-slot-fallback>`
- Odoo 17.0 JavaScript reference: Component composition patterns
- OWL 2.x/3.x slot API changes
