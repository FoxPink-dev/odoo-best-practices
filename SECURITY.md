# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x (Beta) | ✅ |

## Reporting a Vulnerability

We take security seriously. If you discover a security issue, please do **not** open a public issue.

**Contact:** Open a GitHub Issue with the `security` label or email the maintainers directly.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Possible impact

We will respond within 48 hours and work on a fix before public disclosure.

## Scope

- The analyzer is a static analysis tool that reads source code. It does **not** execute Odoo code.
- The GitHub Action runs in an isolated CI environment with read-only permissions.
- The MCP server only reads files from the specified addon directory.
- No telemetry, no network calls, no data collection.

## Best Practices

While using this tool, developers should:
- Review all violations before applying automated suggestions
- Not commit `GITHUB_TOKEN` or other secrets
- Review baseline files (`odoo-baseline.json`) before committing
