# Changelog

## v1.0.0-beta.1 (2026-06-20)

Public beta release of the Odoo Engineering Platform.

### Added

- Static analysis engine with 118 rules across 13 categories
- 12 anti-pattern detectors (search-in-loop, sudo-everywhere, etc.)
- MCP server with 14 tools for AI agent integration (Cursor, Claude Code, OpenCode)
- GitHub Action for automated PR review with annotations and Code Scanning
- SARIF v2.1.0 output for GitHub Security tab
- Baseline suppression system for legacy repository onboarding
- Fix suggestions for each detected violation
- Confidence scores for all violations
- Repository intelligence (models, views, security, graphs)
- Domain knowledge pack for 5 core Odoo models
- Version compatibility guides for Odoo 14–19
- CLI with 5 modes: report, check, index, stats, graph
- 60 official Odoo documentation references

### Fixed

- Encoding declarations for all Python files
- F-string compatibility issues
- Graph indentation and syntax errors
- Checker class implementation with proper rule engine

### Documentation

- Quick Start guide (5-minute setup)
- GitHub Action setup with YAML examples
- MCP configuration for Cursor, Claude Code, OpenCode
- Rule statistics and confidence score explanations
- Baseline system documentation
- Programmatic API examples
