---
name: odoo-best-practices
description: >
  Odoo development best practices and optimization guidelines covering
  module architecture, ORM, security, views, OWL frontend, testing, and
  migration. This skill should be used when writing, reviewing, or
  refactoring Odoo modules to ensure production-grade quality and
  upgrade-safe patterns. Triggers on tasks involving Odoo models, views,
  ORM queries, security rules, OWL components, tests, or data migration.
license: MIT
metadata:
  author: FoxPink
  version: 2.0.0
---

# Odoo Development Best Practices

Comprehensive optimization guide for Odoo module development, covering **13 categories with 136 rules** prioritized by impact. Based on official Odoo documentation (versions 14–19), OCA guidelines, and production deployment experience.

## When to Apply

Reference these guidelines when:

- Writing new Odoo models, fields, or business logic
- Designing view architectures (form, list, kanban, search)
- Implementing security rules (ACL, record rules, field-level)
- Writing OWL components or extending the web client
- Authoring ORM queries — avoid N+1 and prefetching pitfalls
- Writing migration scripts for module upgrades
- Creating automated tests (TransactionCase, HttpCase)
- Reviewing Odoo code for performance, security, or upgrade safety
- Setting up module structure following OCA conventions

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Module Structure & Architecture | CRITICAL | `module-` |
| 2 | ORM & Data Access | CRITICAL | `orm-` |
| 3 | Security | HIGH | `security-` |
| 4 | Views & View Inheritance | MEDIUM-HIGH | `view-` |
| 5 | API & Web Controllers | MEDIUM | `api-` |
| 6 | Data & XML | MEDIUM | `data-` |
| 7 | Performance & Caching | MEDIUM | `perf-` |
| 8 | Testing | MEDIUM | `test-` |
| 9 | Migration & Upgrade | MEDIUM | `migrate-` |
| 10 | OWL Frontend | LOW-MEDIUM | `owl-` |
| 11 | Coding Standards & Lint | LOW | `lint-` / `code-` |
| 12 | i18n & Translations | LOW | `i18n-` |
| 13 | Deployment & Config | LOW | `deploy-` |

---

## 1. Module Structure & Architecture (CRITICAL) — 15 rules

`module-directory-layout`, `module-directory-structure`, `module-manifest`, `module-dependencies`, `module-data-files`, `module-security-groups`, `module-record-rules`, `module-field-access`, `module-ir-cron`, `module-ir-sequence`, `module-ir-actions`, `module-demo-data`, `module-upgrade-migration`, `module-inherit-never-fork`, `module-single-responsibility`

## 2. ORM & Data Access (CRITICAL) — 18 rules

`orm-naming-conventions`, `orm-api-usage`, `orm-computed-fields`, `orm-related-fields`, `orm-onchange`, `orm-constraints`, `orm-model-inheritance`, `orm-order-sorting`, `orm-rec-name`, `orm-defaults`, `orm-selection-fields`, `orm-monetary-fields`, `orm-binary-fields`, `orm-transient-model`, `orm-m2m-through`, `orm-batch-operations`, `orm-field-index`, `orm-no-n-plus-1`

## 3. Security (HIGH) — 11 rules

`security-ir-model-access`, `security-record-rules`, `security-field-groups`, `security-sudo-usage`, `security-check-access-rights`, `security-multi-company`, `security-ir-rule-global`, `security-permissions-inherit`, `security-acl-required`, `security-least-privilege`, `security-record-rules-row-level`

## 4. Views & View Inheritance (MEDIUM-HIGH) — 14 rules

`view-tree-list`, `view-form`, `view-search`, `view-kanban`, `view-graph-pivot`, `view-inheritance`, `view-widget-usage`, `view-button-positions`, `view-dashboard`, `view-calendar`, `view-gantt`, `view-activity`, `view-inherit-not-replace`, `view-new-list-tag`

## 5. API & Web Controllers (MEDIUM) — 6 rules

`api-web-controllers`, `api-external-api`, `api-report-pdf`, `api-email-template`, `api-portal`, `api-web-services`

## 6. Data & XML (MEDIUM) — 8 rules

`data-xml-id-naming`, `data-noupdate`, `data-demo-data`, `data-csv-import`, `data-company-dependent`, `data-default-data`, `data-sequences`, `data-email-templates`

## 7. Performance & Caching (MEDIUM) — 8 rules

`perf-search-optimization`, `perf-batch-operations`, `perf-avoid-n-plus-one`, `perf-index-usage`, `perf-cache-management`, `perf-compute-store`, `perf-computed-dependencies`, `perf-profile-first`

## 8. Testing (MEDIUM) — 10 rules

`test-unit-tests`, `test-httpcase`, `test-tour`, `test-fixtures`, `test-mock-external`, `test-coverage`, `test-tags`, `test-httpcase-for-controllers`, `test-tags-correct`, `test-transactioncase-default`

## 9. Migration & Upgrade (MEDIUM) — 11 rules

`migrate-scripts-directory`, `migrate-three-types`, `migrate-version-bump`, `migrate-pre-raw-sql`, `migrate-post-orm`, `migrate-idempotent`, `migrate-backup-first`, `migrate-noupdate-handling`, `migrate-rename-utils`, `migrate-sequential-versions`, `migrate-openupgrade`

## 10. OWL Frontend (LOW-MEDIUM) — 13 rules

`owl-setup-not-constructor`, `owl-template-naming`, `owl-three-files`, `owl-props-validation`, `owl-usestate-reactive`, `owl-lifecycle-hooks`, `owl-useservice-not-direct`, `owl-slot-composition`, `owl-cleanup-subscriptions`, `owl-patch-not-fork`, `owl-asset-registration`, `owl-t-out-over-t-esc`, `owl-avoid-jquery`

## 11. Coding Standards & Lint (LOW) — 13 rules

`code-python-style`, `code-import-order`, `code-comments`, `code-error-handling`, `code-logging`, `code-versioning`, `code-decorators`, `code-dependencies`, `code-encoding`, `code-api-vs-model`, `lint-pre-commit`, `lint-no-monkey-patch`, `lint-api-decorators`

## 12. i18n & Translations (LOW) — 5 rules

`i18n-translation-files`, `i18n-string-concat`, `i18n-translatable-fields`, `i18n-lazy-translation`, `i18n-language-strings`

## 13. Deployment & Config (LOW) — 4 rules

`deploy-config-params`, `deploy-env-detection`, `deploy-feature-flags`, `deploy-logging-config`

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/orm-no-n-plus-1.md
rules/view-inherit-not-replace.md
```

Each rule file contains:

- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references

## Anti-Pattern Library

Quick-detect common code smells in `bad_patterns/`:

```
bad_patterns/search-inside-loop.md
bad_patterns/sudo-everywhere.md
bad_patterns/write-inside-compute.md
```

## Analyzer (Offline Code Analysis)

Static analysis engine for Odoo addons — use when you need to understand a real codebase. Generates SARIF v2.1.0 output for GitHub Code Scanning and inline suggestions for AI tools.

Key features:
- 14+ tools via MCP for Cursor, Claude Code, OpenCode
- Rich repository intelligence with search_model, search_view, explain_model, etc.
- Fix suggestions for each violation (auto-detected and auto-fixable)
- Baseline suppression for onboarding legacy repositories
- GitHub Action with PR comments and Code Scanning alerts

Usage:
    python -m analyzer.cli path/to/addon                # Markdown report
    python -m analyzer.cli path/to/addon --format json   # JSON report
    python -m analyzer.cli path/to/addon --format sarif  # SARIF for GitHub Code Scanning
    python -m analyzer.cli path/to/addon --check         # AST violations only
    python -m analyzer.cli path/to/addon --check --format sarif -o results.sarif
    python -m analyzer.cli path/to/addon --index         # Build searchable repository_index.json

```
analyzer/
├── cli.py                 # CLI: report / check / index modes
├── checker.py             # Phase 9: AST rule engine (N+1, raw-SQL, sudo, etc.)
├── graph.py               # Inheritance graph + Mermaid output
├── indexer.py             # Phase 7.5: searchable repository_index.json
├── reporter.py            # Combined markdown/JSON report generator
├── store.py               # Unified data access layer (RepositoryStore)
├── mcp_server.py          # MCP protocol server (stdio transport)
└── parsers/
    ├── manifest_parser.py # AST-safe __manifest__.py parsing
    ├── model_parser.py    # Models, Fields, Methods, Decorators, Inheritance
    ├── view_parser.py     # Views, Actions, Menus, Templates
    └── security_parser.py # Security (ACLs, Record Rules, Groups, Categories)
```

### CLI Usage

```bash
# Full analysis report
python -m analyzer.cli path/to/addon

# AST rule violations only (fast)
python -m analyzer.cli path/to/addon --check

# Build searchable index (pseudo-MCP for AI)
python -m analyzer.cli path/to/addon --index -o repo_index

# JSON output
python -m analyzer.cli path/to/addon --format json
```

### RepositoryStore (Programmatic API)

Unified data access layer consumed by CLI, MCP, VS Code, and CI tools:

```python
from analyzer import RepositoryStore

store = RepositoryStore("path/to/addon")
store.load()

# Model queries
store.search_model("sale.order")
store.list_models()
store.fields_for_model("sale.order")
store.methods_for_model("sale.order")
store.model_inheritance_chain("sale.order")

# View queries
store.search_view("sale_order_form")
store.list_views()
store.view_inheritance_chain("sale_order_form")

# Action queries
store.search_action("action_orders")
store.list_actions()

# Security queries
store.list_acls()
store.list_record_rules()
store.models_missing_acl()

# Code checking
store.check_code()
store.violations_by_severity("CRITICAL")

# Domain knowledge
store.explain_model("sale.order")
store.list_knowledge_topics()

# Graphs
store.inheritance_graph_mermaid()
store.dependency_graph()

# Summary
store.repository_summary()
```

### MCP Server (AI Agent Integration)

Exposes all RepositoryStore capabilities via Model Context Protocol for AI agents (Cursor, Claude Code, OpenCode):

**14 tools** available:

| Tool | Description |
|------|-------------|
| `analyze_module` | Full module analysis: models, views, security, dependencies, issues |
| `search_model` | Model definition with fields, methods, inheritance |
| `search_view` | View definition with inheritance chain |
| `search_action` | Action definition with linked views |
| `check_repository` | AST rule engine + security audit + bad pattern detection |
| `explain_model` | Rich model explanation combining index data + knowledge base |
| `list_models` | List all models |
| `list_views` | List all views |
| `list_actions` | List all actions |
| `repository_summary` | High-level repository stats |
| `models_missing_acl` | Security audit: models without ACL entries |
| `inheritance_graph` | Model inheritance graph as Mermaid diagram |
| `build_index` | Rebuild repository index |
| `list_knowledge_topics` | List available domain knowledge topics |

**Configuration** (for Cursor / OpenCode):

```json
{
    "mcpServers": {
        "odoo-analyzer": {
            "command": "python",
            "args": ["-m", "analyzer.mcp_server", "/path/to/addon"]
        }
    }
}
```

## Documentation Reference

Official Odoo docs fetched across all supported versions in `docs/`:

```
docs/14.0_*.md   # ORM, Security, Views, Testing, Actions, Data, Module, HTTP, Reports
docs/15.0_*.md   # Same coverage (backend API layout)
docs/16.0_*.md   # Same coverage
docs/17.0_*.md   # Same coverage
docs/18.0_*.md   # Same coverage
docs/19.0_*.md   # Same coverage (including OWL, guidelines)
```

## Version-Specific Guides

Version-aware rules in `versions/<odoo_version>/`:

```
versions/19/README.md   # Odoo 19: <list> tag, OWL 3 stable
versions/18/README.md   # Odoo 18: Legacy JS removed, OWL 3
versions/17/README.md   # Odoo 17: OWL default
versions/16/README.md   # Odoo 16: Legacy + OWL transition
versions/15/README.md   # Odoo 15: OWL 1.x introduced, t-out, fields.Command
versions/14/README.md   # Odoo 14: Pre-OWL classic, Widget-only, last version before transition
```

## Knowledge Pack

Domain knowledge for 12 core Odoo models in `knowledge/`:

```
knowledge/sale.order.md
knowledge/account.move.md
knowledge/account.payment.md
knowledge/stock.picking.md
knowledge/res.partner.md
knowledge/res.users.md
knowledge/product.product.md
knowledge/crm.lead.md
knowledge/purchase.order.md
knowledge/hr.employee.md
knowledge/project.task.md
knowledge/mail.message.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
