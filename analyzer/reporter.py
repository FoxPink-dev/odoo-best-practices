# -*- coding: utf-8 -*-
import json
import os
from .parsers import ManifestParser, ModelParser, ViewParser, SecurityParser
from .graph import InheritanceGraph, build_graph, graph_to_mermaid
from .checker import Checker


class Reporter:
    """Combine all parser results into a structured report."""

    def __init__(self, addon_dir):
        self.addon_dir = os.path.abspath(addon_dir)
        self.addon_name = os.path.basename(self.addon_dir)
        self.results = {
            "addon": self.addon_name,
            "path": self.addon_dir,
            "manifest": {},
            "models": [],
            "fields": [],
            "methods": [],
            "views": [],
            "actions": [],
            "menus": [],
            "templates": [],
            "acls": [],
            "record_rules": [],
            "groups": [],
            "categories": [],
            "graph": {},
            "summary": {},
            "issues": [],
        }

        # Parsers
        self.mparser = ManifestParser()
        self.moparser = ModelParser()
        self.vparser = ViewParser()
        self.sparser = SecurityParser()

    def run(self):
        """Run all parsers and build report."""
        self._parse_manifest()
        self._parse_models()
        self._parse_views()
        self._parse_security()
        self._build_graphs()
        self._build_summary()
        self._check_issues()
        self._run_rule_engine()
        return self.results

    def run_check_only(self):
        """Run only the rule engine (no full report)."""
        self._parse_manifest()
        self._parse_models()
        self._parse_views()
        self._parse_security()
        self._run_rule_engine()
        return self.results["check_results"]

    def _run_rule_engine(self):
        """Run the AST-based rule engine on parsed data."""
        checker = Checker(self.results)
        violations = checker.run_all()
        self.results["check_results"] = {
            "violations": violations,
            "summary": checker.summary(),
            "by_severity": {
                k: len(v) for k, v in checker.by_severity().items()
            },
        }

    def _parse_manifest(self):
        manifests = self.mparser.find_manifests(self.addon_dir)
        if self.addon_name in manifests:
            self.results["manifest"] = self.mparser.parse_manifest(
                manifests[self.addon_name]
            )

    def _parse_models(self):
        self.moparser.parse_addon(self.addon_dir)
        self.results["models"] = self.moparser.models
        self.results["fields"] = self.moparser.fields
        self.results["methods"] = self.moparser.methods

    def _parse_views(self):
        self.vparser.parse_addon(self.addon_dir)
        self.results["views"] = self.vparser.views
        self.results["actions"] = self.vparser.actions
        self.results["menus"] = self.vparser.menus
        self.results["templates"] = self.vparser.templates

    def _parse_security(self):
        self.sparser.parse_addon(self.addon_dir)
        self.results["acls"] = self.sparser.acls
        self.results["record_rules"] = self.sparser.record_rules
        self.results["groups"] = self.sparser.groups
        self.results["categories"] = self.sparser.categories

    def _build_graphs(self):
        model_summary = self.moparser.get_model_summary()
        module_deps = {self.addon_name: self.results["manifest"].get("depends", [])}
        self.results["graph"] = build_graph(model_summary, module_deps)

    def _build_summary(self):
        """Build a concise summary of the addon analysis."""
        models = self.results["models"]
        fields = self.results["fields"]
        methods = self.results["methods"]
        views = self.results["views"]
        acls = self.results["acls"]

        self.results["summary"] = {
            "module_name": self.addon_name,
            "manifest_version": self.results["manifest"].get("version", "unknown"),
            "dependencies": self.results["manifest"].get("depends", []),
            "models": {
                "total": len(models),
                "with_inheritance": sum(
                    1 for m in models.values() if m.get("_inherit", [])
                ),
                "new_models": sum(
                    1 for m in models.values() if m.get("_name") and not m.get("_inherit", [])
                ),
            },
            "fields": {
                "total": sum(len(f) for f in fields.values()),
                "per_model": {m: len(f) for m, f in fields.items()},
            },
            "methods": {
                "total": sum(len(m) for m in methods.values()),
                "decorated": sum(
                    1 for ml in methods.values()
                    for m in ml if m.get("decorators")
                ),
            },
            "views": {
                "total": len(views),
                "by_type": self._count_by(views, "type"),
                "inherit_only": sum(1 for v in views if v.get("inherit_id")),
            },
            "actions": {"total": len(self.results["actions"])},
            "menus": {"total": len(self.results["menus"])},
            "security": {
                "acls": len(acls),
                "groups": len(self.results["groups"]),
                "record_rules": len(self.results["record_rules"]),
                "models_missing_acl": self._models_missing_acl(),
            },
        }

    def _count_by(self, items, key):
        """Count items grouped by a key value."""
        counts = {}
        for item in items:
            k = item.get(key, "unknown")
            counts[k] = counts.get(k, 0) + 1
        return counts

    def _models_missing_acl(self):
        """Find models that don't have corresponding ACL entries."""
        declared = set(self.results["models"].keys())
        acl_models = set()
        for acl in self.results["acls"]:
            model_ref = acl.get("model_id", "")
            if model_ref:
                # Handle "model_<name>" XML-ID convention (e.g. model_product_template)
                if model_ref.startswith("model_"):
                    acl_models.add(model_ref[6:].replace("_", "."))
                else:
                    acl_models.add(model_ref.replace("_", "."))
        return list(declared - acl_models)

    def _check_issues(self):
        """Detect potential issues in the addon codebase."""
        issues = []

        # Models without ACL
        missing_acl = self._models_missing_acl()
        for m in missing_acl:
            issues.append({
                "severity": "CRITICAL",
                "rule": "security-acl-required",
                "message": "Model '%s' has no ACL entry" % m,
                "model": m,
            })

        # Models without _description
        for name, info in self.results["models"].items():
            if not info.get("_description"):
                issues.append({
                    "severity": "LOW",
                    "rule": "code-docstring-models",
                    "message": "Model '%s' has no _description" % name,
                    "model": name,
                })

        # Check for unsafe patterns
        for model_name, methods in self.results["methods"].items():
            for method in methods:
                decorators = method.get("decorators", [])
                # write() inside compute
                if method["name"] == "write" and any("api.depends" in d for d in decorators):
                    issues.append({
                        "severity": "HIGH",
                        "rule": "orm-computed-fields",
                        "message": "Model '%s': write() with @api.depends" % model_name,
                        "model": model_name,
                        "method": method["name"],
                    })

        self.results["issues"] = issues

    def to_json(self, indent=2):
        """Serialize results to JSON."""
        # Cast non-serializable types
        def _serialize(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError("Type %s not serializable" % type(obj))

        return json.dumps(self.results, indent=indent, default=_serialize)

    def to_markdown(self):
        """Generate a human-readable markdown report."""
        s = self.results["summary"]
        lines = [
            f"# Repository Analysis: {self.addon_name}\n",
        ]

        # Module info
        lines.append("## Module Info\n")
        lines.append(f"- **Version**: {s.get('manifest_version', 'unknown')}")
        lines.append(f"- **Dependencies**: {', '.join(s.get('dependencies', []))}")
        lines.append("")

        # Models
        lines.append("## Models\n")
        lines.append(f"- Total: **{s['models']['total']}**")
        lines.append(f"- New (own models): **{s['models']['new_models']}**")
        lines.append(f"- With inheritance: **{s['models']['with_inheritance']}**")
        lines.append("")

        model_list = self.results.get("models", {})
        if model_list:
            lines.append("### Model List\n")
            lines.append("| Tech Name | Class | File | Inherit | Fields |")
            lines.append("|-----------|-------|------|---------|--------|")
            for name, info in model_list.items():
                inherit_str = ", ".join(info.get("inherit", [])) or "-"
                fields_count = len(self.results["fields"].get(name, []))
                lines.append(
                    f"| {name} | {info['class_name']} | {info['file']} | {inherit_str} | {fields_count} |"
                )
            lines.append("")

        # Inheritance Graph (Mermaid)
        graph = self.results.get("graph", {})
        if graph:
            lines.append("### Inheritance Graph\n")
            lines.append(graph_to_mermaid(graph, "inheritance"))
            lines.append("")

        # Views
        views = self.results.get("views", [])
        if views:
            lines.append("## Views\n")
            lines.append(f"- Total: **{len(views)}**")
            by_type = s.get("views", {}).get("by_type", {})
            lines.append(f"- Types: {', '.join(f'{k}={v}' for k, v in sorted(by_type.items()))}")
            inherit_only = s.get("views", {}).get("inherit_only", 0)
            if inherit_only:
                lines.append(f"- Inheritance views: **{inherit_only}**")
            lines.append("")
            lines.append("| ID | Name | Model | Type | Inherits |")
            lines.append("|----|------|-------|------|----------|")
            for v in views[:20]:  # limit table
                lines.append(
                    f"| {v['id']} | {v['name']} | {v['model']} | {v['type']} | {v.get('inherit_id', '-')} |"
                )
            lines.append("")

        # Security
        acls = self.results.get("acls", [])
        if acls:
            lines.append("## Security\n")
            lines.append(f"- ACLs: **{len(acls)}**")
            lines.append(f"- Groups: **{s.get('security', {}).get('groups', 0)}**")
            lines.append(f"- Record Rules: **{s.get('security', {}).get('record_rules', 0)}**")
            lines.append("")
            lines.append("### ACLs\n")
            lines.append("| ID | Model | Group | Read | Write | Create | Unlink |")
            lines.append("|----|-------|-------|------|-------|--------|--------|")
            for a in acls[:15]:
                lines.append(
                    f"| {a['id']} | {a['model_id']} | {a['group_id']} | {a['perm_read']} | {a['perm_write']} | {a['perm_create']} | {a['perm_unlink']} |"
                )
            lines.append("")

        # Issues
        issues = self.results.get("issues", [])
        if issues:
            lines.append("## Issues Detected\n")
            lines.append("| Severity | Rule | Message |")
            lines.append("|----------|------|---------|")
            for issue in issues:
                lines.append(
                    f"| **{issue['severity']}** | {issue['rule']} | {issue['message']} |"
                )
            lines.append("")
        else:
            lines.append("## Issues\n\nNo issues detected.\n")

        return "\n".join(lines)

    def to_markdown_issues(self):
        """Generate a markdown report with issues/violations only."""
        parts = []
        issues = self.results.get("issues", [])
        if issues:
            parts.append("## Issues Detected\n")
            parts.append("| Severity | Rule | Message |")
            parts.append("|----------|------|---------|")
            for issue in issues:
                parts.append(
                    f"| **{issue['severity']}** | {issue['rule']} | {issue['message']} |"
                )
            parts.append("")
        else:
            parts.append("## Issues\n\nNo issues detected.\n")

        check_results = self.results.get("check_results", {})
        violations = check_results.get("violations", [])
        if violations:
            parts.append("## Violations\n")
            parts.append("| Severity | Rule | File | Line | Message |")
            parts.append("|----------|------|------|------|---------|")
            for v in violations:
                fname = v.get("file", "")
                line = v.get("line", "?")
                parts.append(
                    f"| **{v['severity']}** | {v['rule']} | {fname}:{line} | {v['message']} |"
                )
            parts.append("")
        else:
            parts.append("## Violations\n\nNo violations detected.\n")

        return "\n".join(parts)
