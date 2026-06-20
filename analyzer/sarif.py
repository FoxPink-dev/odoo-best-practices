# -*- coding: utf-8 -*-
"""
SARIF v2.1.0 report generator for the Odoo checker.

Converts checker violations into SARIF format for GitHub Code Scanning
integration and other SARIF-compatible tools.

Usage:
    from analyzer.sarif import violations_to_sarif
    sarif_doc = violations_to_sarif(violations, tool_info)
"""

import json
from .constants import SEVERITY_TO_LEVEL

SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"

# Rule metadata catalog — extends what the checker produces
# Includes fix suggestions for each rule
RULE_CATALOG = {
    "security-acl-required": {
        "id": "security-acl-required",
        "shortDescription": "Model missing ACL entry",
        "fullDescription": "A model is declared but has no corresponding ir.model.access ACL entry. Without ACLs, no user (except superuser) can access the model.",
        "defaultLevel": "error",
        "properties": {
            "category": "security",
            "cwe": "CWE-862",
            "tags": ["security", "access-control"],
        },
        "helpUri": "https://github.com/FoxPink-dev/odoo-best-practices/blob/main/rules/security-acl-required.md",
        "fixSuggestion": {
            "title": "Create default ACL for new model",
            "description": "Add an ir.model.access record for this model to grant access to specific user groups or all users if needed.",
            "example": {
                "bad": "Model declared but no ACL entry",
                "good": "Add ACL entry for the model in security/ir.model.access.csv or through the UI",
            },
        },
    },
    "orm-no-n-plus-1": {
        "id": "orm-no-n-plus-1",
        "shortDescription": "Search or browse inside loop (N+1 query)",
        "fullDescription": "Calling search() or browse() inside a for-loop causes N+1 database queries. Use search_read(), prefetch, or batch outside the loop.",
        "defaultLevel": "error",
        "properties": {
            "category": "orm",
            "cwe": "CWE-400",
            "tags": ["performance", "orm", "scalability"],
        },
        "helpUri": "https://github.com/FoxPink-dev/odoo-best-practices/blob/main/rules/orm-no-n-plus-1.md",
        "fixSuggestion": {
            "title": "Replace in-loop search with batch fetch",
            "description": "Move the search() call outside the loop and use prefetch or batch operations to reduce database queries.",
            "example": {
                "bad": "for rec in self:\n    orders = self.env['sale.order'].search([])",
                "good": "orders = self.env['sale.order'].search([])",
            },
        },
    },
    "orm-raw-sql": {
        "id": "orm-raw-sql",
        "shortDescription": "Raw SQL used without justification",
        "fullDescription": "Raw SQL (self.env.cr.execute) bypasses Odoo ORM security, multi-company rules, and record rules. Use ORM methods instead.",
        "defaultLevel": "error",
        "properties": {
            "category": "orm",
            "cwe": "CWE-89",
            "tags": ["security", "orm"],
        },
    },
    "security-sudo-usage": {
        "id": "security-sudo-usage",
        "shortDescription": "sudo() call bypasses access control",
        "fullDescription": "Using sudo() bypasses all security rules. Ensure the operation is intentionally privileged.",
        "defaultLevel": "error",
        "properties": {
            "category": "security",
            "cwe": "CWE-862",
            "tags": ["security", "access-control"],
        },
    },
    "orm-unindexed-foreign-key": {
        "id": "orm-unindexed-foreign-key",
        "shortDescription": "Foreign key field without index",
        "fullDescription": "Many2one fields should have index=True for performance on large datasets, especially for frequently filtered fields.",
        "defaultLevel": "warning",
        "properties": {
            "category": "orm",
            "cwe": "CWE-400",
            "tags": ["performance", "orm"],
        },
    },
    "security-write-in-compute": {
        "id": "security-write-in-compute",
        "shortDescription": "write() called inside a compute method",
        "fullDescription": "Calling write() inside a @api.depends compute method causes recursion. Assign values directly instead.",
        "defaultLevel": "error",
        "properties": {
            "category": "orm",
            "cwe": "CWE-835",
            "tags": ["orm", "bug"],
        },
    },
    "code-commit-in-business": {
        "id": "code-commit-in-business",
        "shortDescription": "cr.commit() in business logic",
        "fullDescription": "Explicit cr.commit() in business code breaks Odoo's transaction management and can cause partial updates on errors.",
        "defaultLevel": "error",
        "properties": {
            "category": "code",
            "cwe": "CWE-665",
            "tags": ["transaction", "data-integrity"],
        },
    },
}

DEFAULT_RULE = {
    "id": "unknown-rule",
    "shortDescription": "Unknown rule violation",
    "fullDescription": "A code violation was detected but has no SARIF rule metadata.",
    "defaultLevel": "warning",
    "properties": {
        "category": "unknown",
        "tags": [],
    },
}


def violations_to_sarif(violations, tool_info=None):
    """Convert checker violations to SARIF v2.1.0 document.

    Args:
        violations: List of violation dicts from Checker.run_all()
        tool_info: Dict with 'name', 'version', 'informationUri' keys.

    Returns:
        dict: SARIF v2.1.0 document.
    """
    if tool_info is None:
        tool_info = {
            "name": "odoo-analyzer",
            "version": "2.1.0",
            "informationUri": "https://github.com/FoxPink-dev/odoo-best-practices",
        }

    tool = {
        "driver": {
            "name": tool_info["name"],
            "version": tool_info["version"],
            "informationUri": tool_info.get("informationUri", ""),
            "rules": [],
        }
    }

    results = []
    seen_rules = set()

    for v in violations:
        rule_id = v.get("rule", "unknown-rule")
        severity = v.get("severity", "LOW").upper()
        level = SEVERITY_TO_LEVEL.get(severity, "note")
        message = v.get("message", "No description")
        file_path = v.get("file", "")
        line_num = v.get("line", 1)

        # Track unique rules for the rules array
        if rule_id not in seen_rules:
            seen_rules.add(rule_id)
            rule_meta = RULE_CATALOG.get(rule_id, DEFAULT_RULE)
            rule_entry = {
                "id": rule_id,
                "shortDescription": {"text": rule_meta["shortDescription"]},
                "fullDescription": {"text": rule_meta.get("fullDescription", message)},
                "defaultConfiguration": {"level": level},
                "helpUri": "https://github.com/FoxPink-dev/odoo-best-practices/blob/main/rules/%s.md" % rule_id,
                "properties": rule_meta.get("properties", {}),
            }
            tool["driver"]["rules"].append(rule_entry)

        result = {
            "ruleId": rule_id,
            "ruleIndex": list(seen_rules).index(rule_id),
            "level": level,
            "message": {"text": message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_path,
                        },
                        "region": {
                            "startLine": line_num,
                        },
                    }
                }
            ],
            "properties": {
                "severity": severity,
            },
        }

        # Add fix suggestion if available
        rule_meta = RULE_CATALOG.get(rule_id)
        if rule_meta and "fixSuggestion" in rule_meta:
            result["fixSuggestion"] = rule_meta["fixSuggestion"]

        results.append(result)

    return {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": tool,
                "results": results,
                "columnKind": "utf16CodeUnits",
                "properties": {
                    "analyzed": True,
                },
            }
        ],
    }


def write_sarif(violations, output_path, tool_info=None):
    """Generate and write a SARIF report to disk.

    Args:
        violations: List of violation dicts.
        output_path: Path to write the .sarif file.
        tool_info: Optional tool metadata.
    """
    doc = violations_to_sarif(violations, tool_info=tool_info)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    return output_path
