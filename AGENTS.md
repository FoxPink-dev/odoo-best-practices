---
name: odoo-best-practices
description: >
  Odoo development best practices and optimization guidelines covering
  module architecture, ORM, security, views, OWL frontend, testing, API,
  data, i18n, deployment, and migration. Covers Odoo 14–19.
license: MIT
metadata:
  author: FoxPink
  version: 2.0.0
---

# Odoo Development Best Practices — Full Reference

> **136 rules** across 13 categories with anti-pattern detection, version-specific guides, documentation references, domain knowledge pack, and AI IDE integration.

## Structure

```
odoo-best-practices/
├── SKILL.md                      # Entry point — rule index + triggers
├── AGENTS.md                     # This file — full compiled reference
├── README.md                     # Project overview
├── rules/                        # 136 detailed rule files
│   ├── module-*                  # Module architecture (CRITICAL)
│   ├── orm-*                     # ORM & data access (CRITICAL)
│   ├── security-*                # Security (HIGH)
│   ├── view-*                    # Views & inheritance (MED-HIGH)
│   ├── api-*                     # API & web controllers (MEDIUM)
│   ├── data-*                    # Data & XML (MEDIUM)
│   ├── perf-*                    # Performance (MEDIUM)
│   ├── test-*                    # Testing (MEDIUM)
│   ├── migrate-*                 # Migration (MEDIUM)
│   ├── owl-*                     # OWL frontend (LOW-MED)
│   ├── code-* / lint-*           # Coding standards (LOW)
│   ├── i18n-*                    # i18n & translations (LOW)
│   └── deploy-*                  # Deployment & config (LOW)
├── bad_patterns/                 # 12 anti-pattern detectors
├── versions/
│   ├── 14/ README.md             # Odoo 14: Legacy widgets, pre-OWL
│   ├── 15/ README.md             # Odoo 15: OWL 1.x, t-out, fields.Command
│   ├── 16/ README.md             # Odoo 16 specifics
│   ├── 17/ README.md             # Odoo 17 specifics
│   ├── 18/ README.md             # Odoo 18 specifics
│   └── 19/ README.md             # Odoo 19 specifics
├── docs/                         # 50 official documentation refs
│   ├── 14.0_*.md                 # Odoo 14 dev reference
│   ├── 15.0_*.md                 # Odoo 15 dev reference
│   ├── 16.0_*.md                 # Odoo 16 dev reference
│   ├── 17.0_*.md                 # Odoo 17 dev reference
│   ├── 18.0_*.md                 # Odoo 18 dev reference
│   └── 19.0_*.md                 # Odoo 19 dev reference
├── knowledge/                    # Domain knowledge pack (12 models)
│   ├── sale.order.md
│   ├── account.move.md
│   ├── account.payment.md
│   ├── stock.picking.md
│   ├── res.partner.md
│   ├── res.users.md
│   ├── product.product.md
│   ├── crm.lead.md
│   ├── purchase.order.md
│   ├── hr.employee.md
│   ├── project.task.md
│   └── mail.message.md
├── analyzer/                     # Static analysis engine
│   ├── store.py                  # RepositoryStore (unified API layer)
│   ├── mcp_server.py             # MCP protocol server (14 tools)
│   ├── checker.py                # AST rule engine
│   ├── indexer.py                # Repository index builder
│   ├── reporter.py               # Combined report generator
│   ├── cli.py                    # CLI: report / check / index
│   ├── graph.py                  # Inheritance + dependency graphs
│   └── parsers/
│       ├── manifest_parser.py
│       ├── model_parser.py
│       ├── view_parser.py
│       └── security_parser.py
├── .github/                      # GitHub Action + CI
│   └── workflows/
│       ├── odoo-review.yml
│       ├── publish-pypi.yml
│       └── publish-npm.yml
├── package.json                  # npm wrapper for `npx odoo-review`
├── bin/                          # npm CLI entry point
└── .npmignore                    # npm publish filter
```

## Rule Categories

### 1. Module Structure & Architecture (CRITICAL) — 15 rules
module-directory-layout, module-directory-structure, module-manifest, module-dependencies, module-data-files, module-security-groups, module-record-rules, module-field-access, module-ir-cron, module-ir-sequence, module-ir-actions, module-demo-data, module-upgrade-migration, module-inherit-never-fork, module-single-responsibility

## Fix Suggestions

Each violation includes actionable fix suggestions to help developers quickly resolve issues:

```json
{
  "violation": {
    "rule": "search-inside-loop",
    "severity": "CRITICAL",
    "message": "search() inside loop",
    "file": "models/order.py",
    "line": 54
  },
  "fixSuggestion": {
    "title": "Replace in-loop search with batch fetch",
    "description": "Move the search() call outside the loop and use prefetch or batch operations to reduce database queries.",
    "example": {
      "bad": "for rec in self:\n    orders = self.env['sale.order'].search([])",
      "good": "orders = self.env['sale.order'].search([])"
    }
  }
}
```

Fix suggestions are available in:
- SARIF reports (for GitHub Code Scanning)
- MCP `check_repository` tool calls
- GitHub Action PR comments
- All analyzer output formats (Markdown, JSON, SARIF)

### 2. ORM & Data Access (CRITICAL) — 18 rules
orm-naming-conventions, orm-api-usage, orm-computed-fields, orm-related-fields, orm-onchange, orm-constraints, orm-model-inheritance, orm-order-sorting, orm-rec-name, orm-defaults, orm-selection-fields, orm-monetary-fields, orm-binary-fields, orm-transient-model, orm-m2m-through, orm-batch-operations, orm-field-index, orm-no-n-plus-1

### 3. Security (HIGH) — 11 rules
security-ir-model-access, security-record-rules, security-field-groups, security-sudo-usage, security-check-access-rights, security-multi-company, security-ir-rule-global, security-permissions-inherit, security-acl-required, security-least-privilege, security-record-rules-row-level

### 4. Views & View Inheritance (MEDIUM-HIGH) — 14 rules
view-tree-list, view-form, view-search, view-kanban, view-graph-pivot, view-inheritance, view-widget-usage, view-button-positions, view-dashboard, view-calendar, view-gantt, view-activity, view-inherit-not-replace, view-new-list-tag

### 5. API & Web Controllers (MEDIUM) — 6 rules
api-web-controllers, api-external-api, api-report-pdf, api-email-template, api-portal, api-web-services

### 6. Data & XML (MEDIUM) — 8 rules
data-xml-id-naming, data-noupdate, data-demo-data, data-csv-import, data-company-dependent, data-default-data, data-sequences, data-email-templates

### 7. Performance & Caching (MEDIUM) — 8 rules
perf-search-optimization, perf-batch-operations, perf-avoid-n-plus-one, perf-index-usage, perf-cache-management, perf-compute-store, perf-computed-dependencies, perf-profile-first

### 8. Testing (MEDIUM) — 10 rules
test-unit-tests, test-httpcase, test-tour, test-fixtures, test-mock-external, test-coverage, test-tags, test-httpcase-for-controllers, test-tags-correct, test-transactioncase-default

### 9. Migration & Upgrade (MEDIUM) — 11 rules
migrate-scripts-directory, migrate-three-types, migrate-version-bump, migrate-pre-raw-sql, migrate-post-orm, migrate-idempotent, migrate-backup-first, migrate-noupdate-handling, migrate-rename-utils, migrate-sequential-versions, migrate-openupgrade

### 10. OWL Frontend (LOW-MEDIUM) — 13 rules
owl-setup-not-constructor, owl-template-naming, owl-three-files, owl-props-validation, owl-usestate-reactive, owl-lifecycle-hooks, owl-useservice-not-direct, owl-slot-composition, owl-cleanup-subscriptions, owl-patch-not-fork, owl-asset-registration, owl-t-out-over-t-esc, owl-avoid-jquery

### 11. Coding Standards & Lint (LOW) — 13 rules
code-python-style, code-import-order, code-comments, code-error-handling, code-logging, code-versioning, code-decorators, code-dependencies, code-encoding, code-api-vs-model, lint-api-decorators, lint-no-monkey-patch, lint-pre-commit

### 12. i18n & Translations (LOW) — 5 rules
i18n-translation-files, i18n-string-concat, i18n-translatable-fields, i18n-lazy-translation, i18n-language-strings

### 13. Deployment & Config (LOW) — 4 rules
deploy-config-params, deploy-env-detection, deploy-feature-flags, deploy-logging-config

## Anti-Pattern Detection

| Pattern | Severity | Rule |
|---------|----------|------|
| Raw SQL without reason | HIGH | bad_patterns/raw-sql-without-reason |
| search() inside loop | CRITICAL | bad_patterns/search-inside-loop |
| write() inside compute | HIGH | bad_patterns/write-inside-compute |
| sudo() everywhere | HIGH | bad_patterns/sudo-everywhere |
| Replace entire view | HIGH | bad_patterns/replace-entire-view |
| browse() inside loop | CRITICAL | bad_patterns/browse-inside-loop |
| Missing ACL for new model | CRITICAL | bad_patterns/no-acl-for-new-model |
| cr.commit() in business code | HIGH | bad_patterns/commit-in-business-code |
| Unindexed foreign key | MEDIUM | bad_patterns/unindexed-foreign-key |
| Non-translatable user field | MEDIUM | bad_patterns/translate-false-for-user-strings |
| Context not propagated | MEDIUM | bad_patterns/copy-context-instead-of-propagate |
| _nocheck bypass | MEDIUM | bad_patterns/nocheck-in-constrains |

## Version Compatibility (14–19)

| Feature | 14 | 15 | 16 | 17 | 18 | 19 |
|---------|----|----|----|----|----|----|
| Legacy Widget | ✅ | ✅ | ✅ | ⚠️ Deprecated | ❌ Removed | ❌ |
| OWL 2.x | ❌ | ❌ | ✅ Default | ✅ Default | ❌ | ❌ |
| OWL 3.x | ❌ | ❌ | ❌ | ❌ | ✅ Transition | ✅ Stable |
| `<tree>` tag | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Legacy |
| `<list>` tag | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Canonical |
| `t-esc` | ✅ | ✅ | ✅ | ⚠️ Deprecated | ❌ Removed | ❌ |
| `t-out` | ❌ | ❌ | ❌ | ✅ | ✅ Required | ✅ Required |
| `@api.one` | ❌ Removed | ❌ | ❌ | ❌ | ❌ | ❌ |
| `models.Constraint` | ❌ | ❌ | ❌ | ❌ | ✅ New | ✅ Stable |
| `search_fetch()` | ❌ | ❌ | ❌ | ❌ | ✅ New | ✅ Stable |
| ORM `flush()` | ❌ | ❌ | ❌ | ❌ | ✅ New | ✅ Stable |
| Web/Controllers moved | backend/ | backend/ | backend/ | backend/ | backend/ | addons/ |

## Documentation Reference

50 official Odoo documentation files fetched in `docs/`:

| Version | Pages | Key Content |
|---------|-------|-------------|
| 14.0 | 10 | ORM, Security, Views, Testing, Actions, Data, Module, HTTP, Reports, Guidelines |
| 15.0 | 10 | Same (backend API layout) |
| 16.0 | 10 | Same |
| 17.0 | 10 | Same |
| 18.0 | 10 | Same |
| 19.0 | 10 | Same (including OWL reference, coding guidelines) |

## Getting Started

```bash
# The SKILL.md description triggers auto-loading on Odoo-related tasks

# Read individual rules:
cat rules/orm-naming-conventions.md

# Read anti-pattern detectors:
cat bad_patterns/search-inside-loop.md

# Read version-specific guide:
cat versions/19/README.md

# Read domain knowledge:
cat knowledge/sale.order.md
```
