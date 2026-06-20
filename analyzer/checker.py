# -*- coding: utf-8 -*-
"""Phase 9 - Odoo Rule Engine (AST-based code checker).

Walks parsed Python AST + parsed metadata to detect rule violations.
Each rule is a stateless check function that receives analysis context.
"""

from .graph import InheritanceGraph


class Checker:
    """Detect potential issues in the addon codebase."""

    def __init__(self, store_or_results):
        self.results = store_or_results if isinstance(store_or_results, dict) else {}
        self.violations = []
        self._summary = {}
        self._by_severity = {}

    def run_all(self):
        """Run all checks and return violations with confidence scores."""
        self.violations = []
        self._check_models_missing_acl()
        self._check_nplus1()
        self._check_raw_sql()
        self._check_sudo()
        self._compute_summary()
        return self.violations

    def _check_models_missing_acl(self):
        models = self.results.get("models", {})
        model_names = list(models.keys())
        acls = self.results.get("acls", [])
        acl_models = set(a.get("model", "") for a in acls)

        for m in model_names:
            if m not in acl_models:
                self.violations.append({
                    "severity": "CRITICAL",
                    "rule": "security-acl-required",
                    "message": "Model '%s' has no ACL entry" % (m,),
                    "file": models[m].get("file", ""),
                    "line": 1,
                    "confidence": 95,
                })

    def _check_nplus1(self):
        methods = self.results.get("methods", {})
        for method_name, method_info in methods.items():
            code = method_info.get("code", "")
            if "for " in code and "search(" in code:
                self.violations.append({
                    "severity": "CRITICAL",
                    "rule": "orm-no-n-plus-1",
                    "message": "search() inside loop in method '%s'" % (method_name,),
                    "file": method_info.get("file", ""),
                    "line": method_info.get("line", 1),
                    "confidence": 85,
                })

    def _check_raw_sql(self):
        methods = self.results.get("methods", {})
        for method_name, method_info in methods.items():
            code = method_info.get("code", "")
            if "cr.execute" in code or "execute(" in code:
                self.violations.append({
                    "severity": "HIGH",
                    "rule": "orm-raw-sql",
                    "message": "Raw SQL query in method '%s'" % (method_name,),
                    "file": method_info.get("file", ""),
                    "line": method_info.get("line", 1),
                    "confidence": 70,
                })

    def _check_sudo(self):
        methods = self.results.get("methods", {})
        for method_name, method_info in methods.items():
            code = method_info.get("code", "")
            lines = code.split("\n")
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if line_stripped.startswith("self.env") and "sudo()" in line_stripped:
                    self.violations.append({
                        "severity": "HIGH",
                        "rule": "orm-sudo-sparingly",
                        "message": "sudo() used in method '%s':%s" % (method_name, method_info.get('line', 1) + i - 1,),
                        "file": method_info.get("file", ""),
                        "line": method_info.get("line", 1) + i - 1,
                        "confidence": 60,
                    })

    def _compute_summary(self):
        by_sev = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for v in self.violations:
            sev = v.get("severity", "LOW")
            if sev in by_sev:
                by_sev[sev] += 1
        self._by_severity = by_sev
        self._summary = {
            "total": len(self.violations),
            "critical": by_sev["CRITICAL"],
            "high": by_sev["HIGH"],
            "medium": by_sev["MEDIUM"],
            "low": by_sev["LOW"],
        }

    def summary(self):
        return self._summary

    def by_severity(self):
        return self._by_severity
