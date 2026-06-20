# Odoo Best Practices — AI-powered Odoo Engineering Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Odoo 14-19](https://img.shields.io/badge/Odoo-14%20to%2019-purple)](https://www.odoo.com)

Static analysis engine + domain knowledge platform + MCP server for Odoo module development. Covers **118 rules**, **12 anti-patterns**, **6 Odoo versions**, and provides **14 MCP tools** for AI-assisted code review.

---

## Quick Start (5 minutes)

```bash
# 1. Clone
git clone https://github.com/FoxPink-dev/odoo-best-practices.git
cd odoo-best-practices

# 2. Run analysis on your Odoo addon
python -m analyzer.cli /path/to/your/addon --check
```

**Expected output:**

```
Models: 12
Fields: 142
Violations: 3 violations found
  CRITICAL: 1
  HIGH:     1
  MEDIUM:   1
  LOW:      0
```

> If you see output like above, the analyzer is working. You just ran your first Odoo analysis in **5 minutes**.

### Try with demo data

```bash
python -m analyzer.cli tests/fixtures/demo_addon --check --format json
```

---

## GitHub Action Setup

### 1. Add workflow file

Create `.github/workflows/odoo-review.yml`:

```yaml
name: Odoo Review
on:
  pull_request:
    paths:
      - '**.py'
      - '**/__manifest__.py'
      - '**/*.xml'
      - '**/security/*.csv'

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - name: Odoo Static Analysis
        uses: ./.github/actions/odoo-review
        with:
          addon-path: '.'
          fail-on-critical: 'true'
          fail-on-high: 'true'
          baseline: "${{ github.event.action == 'opened' || github.event.action == 'reopened' }}"
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload SARIF to Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: odoo-review-results.sarif
          category: odoo-analyzer
        continue-on-error: true
```

### 2. PR Results

After running, you will see in the PR:

| Feature | Display |
|---------|---------|
| PR Comment | Violations table grouped by severity with file:line |
| Annotations | Inline error/warning markers on each code line |
| Code Scanning | SARIF upload → GitHub Security tab |

```

┌─────────────────────────────────────────────┐
│  ## Odoo Analysis Report                     │
│  | Severity | Count |                       │
│  |----------|-------|                       │
│  | 🔴 CRITICAL | 1 |                        │
│  | 🟠 HIGH     | 1 |                        │
│  | 🟡 MEDIUM   | 1 |                        │
│  | **Total**   | **3** |                    │
│                                              │
│  ### 🔴 CRITICAL (1)                         │
│  - **`models/sale.py:42`** — search() inside │
│    loop                                      │
│    <sub>rule: `search-inside-loop`</sub>     │
└─────────────────────────────────────────────┘
```

> **Tip**: On first run against a legacy repo, use `generate-baseline: 'true'` to baseline existing violations.

---

## MCP Server (AI Agent Integration)

### Cursor

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

### Claude Code

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

### OpenCode

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

### 14 MCP Tools Available

| Tool | Description |
|------|-------------|
| `analyze_module` | Full module analysis: models, views, security, dependencies |
| `search_model` | Model definition with fields, methods, inheritance |
| `search_view` | View definition with inheritance chain |
| `search_action` | Action definition with linked views |
| `check_repository` | AST rule engine + security audit |
| `explain_model` | Rich model explanation with knowledge base |
| `list_models` | List all models in repository |
| `list_views` | List all views in repository |
| `list_actions` | List all actions in repository |
| `repository_summary` | High-level repository stats |
| `models_missing_acl` | Security audit: models without ACL |
| `inheritance_graph` | Model inheritance graph as Mermaid |
| `build_index` | Rebuild repository index |
| `list_knowledge_topics` | List domain knowledge topics |

### Example: AI-assisted debugging

```
User: "Why does sale.order have no ACL?"
→ Agent calls `search_model("sale.order")` + `models_missing_acl`
→ "Model sale.order is defined at models/sale.py:10 but has no ACL entry in security/ir.model.access.csv"
```

---

## CLI Reference

```bash
# Full analysis with markdown report
python -m analyzer.cli path/to/addon

# JSON output for CI pipelines
python -m analyzer.cli path/to/addon --format json

# SARIF for GitHub Code Scanning
python -m analyzer.cli path/to/addon --format sarif -o results.sarif

# Quick check (violations only)
python -m analyzer.cli path/to/addon --check

# Check with baseline suppression (legacy repos)
python -m analyzer.cli path/to/addon --check --baseline

# Generate baseline from existing violations
python -m analyzer.cli path/to/addon --baseline

# Build searchable index for AI tools
python -m analyzer.cli path/to/addon --index -o repo_index

# Rule statistics
python -m analyzer.cli path/to/addon --stats

# Inheritance graph (Mermaid format)
python -m analyzer.cli path/to/addon --graph
```

---

## Rule Statistics

```bash
python -m analyzer.cli path/to/addon --stats
```

**Output:**

```
Repository: my_addon
  Models: 12
  Fields: 142
  Views:  8
  Actions: 5
  ACLs:   10
  Record Rules: 3

Violations by severity:
  CRITICAL:  2
  HIGH:      7
  MEDIUM:    13
  LOW:       21
  ─────────────────
  Total:     43

Top rules violated:
  orm-no-n-plus-1 (CRITICAL)    → 3 violations
  orm-raw-sql (HIGH)            → 2 violations
  security-acl (CRITICAL)       → 2 violations
```

---

## Confidence Score

Each violation includes a confidence score to help prioritize review:

```
search-inside-loop
  Severity:   CRITICAL
  Confidence: 98%              ← High accuracy → fix immediately

missing-index
  Severity:   MEDIUM
  Confidence: 60%              ← Possible false positive → review needed
```

| Confidence | Meaning | Action |
|-----------|---------|--------|
| 90-100% | Static analysis certainty | Fix immediately |
| 70-89% | Clear pattern match | Quick review |
| 50-69% | Heuristic-based | Needs verification |
| < 50% | Low confidence | May ignore |

---

## Use Cases

### 1. Code Review Automation

GitHub Action automatically reviews every PR:

```yaml
# .github/workflows/odoo-review.yml
- name: Odoo Review
  uses: ./.github/actions/odoo-review
  with:
    fail-on-critical: 'true'
```

### 2. Legacy Repository Onboarding

```bash
# Step 1: Baseline existing violations
python -m analyzer.cli /path/to/legacy/addon --baseline
# → Creates odoo-baseline.json with 387 accepted violations

# Step 2: Only NEW violations are reported from now on
python -m analyzer.cli /path/to/legacy/addon --check --baseline
# → Only 3 new violations remain
```

### 3. AI-assisted Development

MCP server enables AI agents to understand your Odoo codebase:

```
→ "Explain model sale.order"
→ Agent returns: fields, methods, views, inheritance chain, knowledge docs
```

### 4. CI Pipeline Quality Gate

```yaml
# Fail build if CRITICAL or HIGH violations exist
- name: Quality Gate
  run: |
    python -m analyzer.cli . --check --format json -o report.json
    python -m ci_tools/check_gate.py report.json
```

---

## Baseline System

Enables onboarding legacy repositories without being overwhelmed by existing violations.

```bash
# Generate baseline
python -m analyzer.cli /path/to/addon --baseline

# Check with baseline
python -m analyzer.cli /path/to/addon --check --baseline
```

Baseline data is stored as `odoo-baseline.json`:

```json
{
  "version": 1,
  "addon": "my_addon",
  "timestamp": "2026-06-20T12:00:00Z",
  "total_accepted": 387,
  "accepted": [
    {"rule": "orm-no-n-plus-1", "file": "models/foo.py", "line": 54}
  ]
}
```

---

## Programmatic API

```python
from analyzer import RepositoryStore

store = RepositoryStore("path/to/addon")
store.load()

# Model queries
store.search_model("sale.order")
store.fields_for_model("sale.order")
store.methods_for_model("sale.order")

# Analysis
store.check_code()
store.violations_by_severity("CRITICAL")

# Security audit
store.models_missing_acl()
store.list_acls()

# Graphs
print(store.inheritance_graph_mermaid())

# Summary
print(store.repository_summary())
```

---

## Project Structure

```
odoo-best-practices/
├── SKILL.md                       # Entry point — 14 tool definitions
├── AGENTS.md                      # Full compiled reference
├── README.md                      # This file
├── rules/                         # 118 rule files (13 categories)
├── bad_patterns/                  # 12 anti-pattern detectors
├── knowledge/                     # 5 core model domain files
├── versions/{14,15,16,17,18,19}/ # Version-specific guides
├── docs/                          # 60 official Odoo docs (14-19)
└── analyzer/                      # Python static analysis engine
    ├── cli.py                     # CLI: report / check / index
    ├── checker.py                 # AST rule engine
    ├── indexer.py                 # Repository index
    ├── reporter.py                # Markdown/JSON report
    ├── baseline.py                # Baseline suppression
    ├── sarif.py                   # SARIF v2.1.0 output
    ├── store.py                   # RepositoryStore (unified API)
    ├── mcp_server.py              # MCP protocol server (14 tools)
    ├── graph.py                   # Inheritance + dependency graphs
    └── parsers/
        ├── manifest_parser.py
        ├── model_parser.py
        ├── view_parser.py
        └── security_parser.py
.github/
├── workflows/odoo-review.yml      # GitHub Action workflow
└── actions/odoo-review/           # Custom action
    └── entrypoint.py
.opencode/
└── skill.json                     # OpenCode skill config
```

---

## Version Support

| Version | Status | Key Features |
|---------|--------|-------------|
| 14 | ✅ Legacy | Pre-OWL, Classic Widgets |
| 15 | ✅ Legacy | OWL 1.x introduced |
| 16 | ✅ Stable | OWL 2.x Default |
| 17 | ✅ Stable | OWL Required, t-out |
| 18 | ✅ Current | Legacy JS removed, OWL 3 |
| 19 | ✅ Latest | `<list>` tag canonical |

---

## License

MIT

---

## Portfolio Note

> Built an Odoo Engineering Platform featuring repository intelligence, static analysis, MCP integration, GitHub-native code review, SARIF reporting, baseline suppression, and AI-assisted development workflows for Odoo 14–19.

This project demonstrates:
- **AST parsing** — Python source code analysis
- **Static analysis** — Rule engine, pattern detection
- **DevSecOps** — CI/CD integration, quality gates
- **MCP/AI tooling** — 14 tools for AI agents
- **Rule engine design** — 118 rules across 13 categories
- **Platform engineering** — From CLI to GitHub Action to AI integration
