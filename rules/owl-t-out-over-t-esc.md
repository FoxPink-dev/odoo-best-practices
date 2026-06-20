---
priority: MUST
tags: [owl, qweb, t-esc, t-out, xss, security]
odoo_versions: [16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "rendering content in QWeb"
    includes: ["**/*.xml"]
  - task: "using t-esc in templates"
    includes: ["t-esc"]
---
# Use `t-out` Instead of `t-esc` for User Content

## Description

`t-esc` escapes HTML but is deprecated in Odoo 17+ and removed in Odoo 18+. Use `t-out` for all output expressions. For HTML content that must render unescaped, use `t-out-raw` and sanitize the input first.

## Correct

```xml
<!-- Odoo 17+ : use t-out -->
<span><t t-out="state.userName"/></span>
<span><t t-out="state.message"/></span>

<!-- Only for trusted HTML (sanitized server-side) -->
<div><t t-out-raw="state.sanitizedHtml"/></div>
```

## Incorrect

```xml
<!-- Odoo 17+ deprecated, removed in Odoo 18 -->
<span><t t-esc="state.userName"/></span>      <!-- WRONG: use t-out -->
<span><t t-esc="state.message"/></span>        <!-- WRONG: use t-out -->

<!-- Insecure: raw user input without sanitization -->
<div><t t-out-raw="state.userInput"/></div>    <!-- WRONG: XSS vulnerability -->
```

## Rationale

`t-esc` (escape) was the standard output directive in Odoo ≤16. It was deprecated in Odoo 17 and completely removed in Odoo 18. `t-out` provides the same XSS-safe escaping with better performance and consistency with modern QWeb. `t-out-raw` outputs unescaped HTML — only use with server-side sanitized content to prevent cross-site scripting (XSS) vulnerabilities.

## References

- Odoo 17.0 QWeb reference: `t-out`, `t-esc` deprecation
- Odoo 18.0 QWeb reference: `t-out` replaces `t-esc`
- OWL rendering pipeline: how t-out handles text nodes
