# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Odoo Repository Analyzer — CLI entry point.

Usage:
    python -m analyzer.cli path/to/addon                      # Markdown report
    python -m analyzer.cli path/to/addon --format json         # JSON report
    python -m analyzer.cli path/to/addon --format sarif        # SARIF for Code Scanning
    python -m analyzer.cli path/to/addon --check               # AST violations only
    python -m analyzer.cli path/to/addon --check --baseline    # Check with baseline
    python -m analyzer.cli path/to/addon --baseline            # Generate baseline.json
    python -m analyzer.cli path/to/addon --stats               # Rule statistics
    python -m analyzer.cli path/to/addon --graph               # Inheritance graph
    python -m analyzer.cli path/to/addon --index               # Build repository index
"""

import argparse
import json
import sys
import os

from .reporter import Reporter
from .indexer import RepositoryIndex
from .baseline import Baseline
from .graph import build_graph, graph_to_mermaid


def main():
    parser = argparse.ArgumentParser(
        description="Analyze an Odoo addon directory for repository intelligence."
    )
    parser.add_argument(
        "addon_dir",
        nargs="?",
        help="Path to the Odoo addon directory to analyze",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "both", "sari", "sarif"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (optional; prints to stdout if omitted)",
    )
    parser.add_argument(
        "--issues-only",
        action="store_true",
        help="Only output detected issues from reporter",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run AST rule engine only (fast mode)",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Build repository_index.json (pseudo-MCP for AI)",
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Generate or check against baseline",
    )
    parser.add_argument(
        "--baseline-path",
        help="Path to baseline.json file (default: <addon_dir>/odoo-baseline.json)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show repository statistics summary",
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Show inheritance graph (Mermaid)",
    )
    parser.add_argument(
        "--confidence",
        action="store_true",
        help="Show confidence scores for violations",
    )
    parser.add_argument(
        "--init",
        choices=["opencode", "claude", "cursor", "kiro", "windsurf", "all"],
        help="Generate AI IDE config files for odoo-best-practices in the current project",
    )

    args = parser.parse_args()

    # --- Init mode (generate IDE configs, no addon needed) ---
    if args.init:
        from .init_generator import generate
        results = generate(args.init, ".")
        for ide_name, filepath in results:
            print("Generated %s config: %s" % (ide_name, filepath))
        return 0

    if not args.addon_dir:
        parser.print_usage()
        print("Error: addon_dir is required", file=sys.stderr)
        sys.exit(1)

    addon_path = os.path.abspath(args.addon_dir)

    if not os.path.isdir(addon_path):
        print("Error: '%s' is not a directory" % (addon_path,), file=sys.stderr)
        sys.exit(1)

    # --- Index mode ---
    if args.index:
        print("Indexing addon: %s" % (addon_path,), file=sys.stderr)
        indexer = RepositoryIndex(addon_path)
        index = indexer.build()
        print(indexer.summary(), file=sys.stderr)
        output_path = args.output or "repository_index"
        _write_output(indexer.to_json(), output_path, "json")
        print("\n  AI query examples:", file=sys.stderr)
        print("    indexer.search_model('sale.order')", file=sys.stderr)
        print("    indexer.fields_for_model('res.partner')", file=sys.stderr)
        return 0

    # --- Graph mode ---
    if args.graph:
        print("Generating inheritance graph for: %s" % (addon_path,), file=sys.stderr)
        from .parsers.model_parser import ModelParser
        moparser = ModelParser()
        moparser.parse_addon(addon_path)
        graph = build_graph(moparser.get_model_summary())
        mermaid = graph_to_mermaid(graph)
        print("\n" + mermaid)
        return 0

    # --- Baseline generation mode ---
    if args.baseline and not args.check:
        print("Generating baseline for: %s" % (addon_path,), file=sys.stderr)
        reporter = Reporter(addon_path)
        reporter.run()
        violations = reporter.results.get("check_results", {}).get("violations", [])
        bl = Baseline(addon_path, baseline_path=args.baseline_path)
        baseline = bl.generate(violations)
        print(json.dumps(baseline, indent=2), file=sys.stderr)
        return 0

    # --- Stats mode ---
    if args.stats:
        reporter = Reporter(addon_path)
        results = reporter.run()
        summary = results.get("summary", {})

        check_results = results.get("check_results", {})
        violations = check_results.get("violations", [])
        v_summary = check_results.get("summary", {})

        print("Repository: %s" % (summary.get('module_name', os.path.basename(addon_path)),))
        print("  Models:     %s" % (summary.get('models', {}).get('total', 0),))
        print("  Fields:     %s" % (summary.get('fields', {}).get('total', 0),))
        print("  Views:      %s" % (summary.get('views', {}).get('total', 0),))
        print("  Actions:    %s" % (summary.get('actions', {}).get('total', 0),))
        print("  ACLs:       %s" % (summary.get('security', {}).get('acls', 0),))
        print("  Record Rules: %s" % (summary.get('security', {}).get('record_rules', 0),))
        print()

        v_total = v_summary.get("total", 0)
        if v_total > 0:
            print("Violations by severity:")
            print("  CRITICAL:  %s" % (v_summary.get('critical', 0),))
            print("  HIGH:      %s" % (v_summary.get('high', 0),))
            print("  MEDIUM:    %s" % (v_summary.get('medium', 0),))
            print("  LOW:       %s" % (v_summary.get('low', 0),))
            print("  %s" % ('─' * 16,))
            print("  Total:     %s" % (v_total,))
            print()

            # Top violated rules
            rule_counts = {}
            for v in violations:
                rule = v.get("rule", "unknown")
                rule_counts[rule] = rule_counts.get(rule, 0) + 1
            top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_rules:
                print("Top rules violated:")
                for rule, count in top_rules:
                    sev = "?"
                    for v in violations:
                        if v.get("rule") == rule:
                            sev = v.get("severity", "?")
                            break
                    print("  %s (%s)%s → %s violation(s)" % (rule, sev, ' ' * max(1, 35 - len(rule)), count,))
        else:
            print("  ✅ No violations found.")
        return 0

    # --- Check mode (fast, rule engine only) ---
    if args.check:
        print("Reviewing addon: %s" % (addon_path,), file=sys.stderr)
        reporter = Reporter(addon_path)
        check_results = reporter.run_check_only()
        all_violations = check_results.get("violations", [])
        summary = check_results.get("summary", {})

        # Apply baseline suppression if requested
        violations = all_violations
        known_count = 0
        if args.baseline:
            bl = Baseline(addon_path, baseline_path=args.baseline_path)
            loaded = bl.load()
            if loaded:
                filtered = bl.filter(all_violations)
                violations = filtered["new"]
                known_count = filtered["summary"]["known"]
                print("  Baseline active: %s known violations suppressed" % (known_count,), file=sys.stderr)
            else:
                print("  Warning: no baseline found at %s" % (bl._baseline_path,), file=sys.stderr)

        print("\n  Total violations: %s" % (summary.get('total', 0),), file=sys.stderr)
        if known_count:
            print("  Known (suppressed): %s" % (known_count,), file=sys.stderr)
            print("  New: %s" % (len(violations),), file=sys.stderr)
        print("    CRITICAL: %s" % (summary.get('critical', 0),), file=sys.stderr)
        print("    HIGH:     %s" % (summary.get('high', 0),), file=sys.stderr)
        print("    MEDIUM:   %s" % (summary.get('medium', 0),), file=sys.stderr)
        print("    LOW:      %s" % (summary.get('low', 0),), file=sys.stderr)

        # Output violations table
        sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_violations = sorted(
            violations,
            key=lambda x: sev_order.get(x.get("severity", "LOW"), 99)
        )

        lines = ["# Code Review Results\n", "| Severity | Rule | File | Line | Confidence | Message |",
                 "|----------|------|------|------|------------|---------|"]
        for v in sorted_violations:
            fname = os.path.relpath(v.get("file", ""), addon_path) if v.get("file") else ""
            sev = v.get("severity", "LOW")
            rule = v.get("rule", "?")
            line_num = v.get("line", "?")
            msg = v.get("message", "?")
            conf = v.get("confidence", 50)
            conf_str = "%s%%" % (conf,) if args.confidence else ""
            lines.append("| **%s** | %s | %s:%s | %s | %s |" % (sev, rule, fname, line_num, conf_str, msg,))

        if known_count:
            lines.append("\n*Baseline suppressed %s known violations.*\n" % (known_count,))

        output = "\n".join(lines)

        if args.format == "sari":
            from .sarif import violations_to_sarif
            sarif_doc = violations_to_sarif(violations)
            sarif_doc["runs"][0]["properties"]["baseline"] = {
                "total_violations": summary.get("total", 0),
                "suppressed": known_count,
                "reported": len(violations),
            }
            sarif_json = json.dumps(sarif_doc, indent=2)
            _write_output(sarif_json, args.output, "sari")
        else:
            _write_output(output, args.output, "md")
        return 0

    # --- Full report mode ---
    print("Analyzing addon: %s" % (addon_path,), file=sys.stderr)
    reporter = Reporter(addon_path)
    results = reporter.run()
    summary = results.get("summary", {})
    check_summary = results.get("check_results", {}).get("summary", {})

    print("\n  Module:     %s" % (summary.get('module_name', 'unknown'),), file=sys.stderr)
    print("  Version:    %s" % (summary.get('manifest_version', 'unknown'),), file=sys.stderr)
    print("  Models:     %s" % (summary.get('models', {}).get('total', 0),), file=sys.stderr)
    print("  Fields:     %s" % (summary.get('fields', {}).get('total', 0),), file=sys.stderr)
    print("  Views:      %s" % (summary.get('views', {}).get('total', 0),), file=sys.stderr)
    print("  ACLs:       %s" % (summary.get('security', {}).get('acls', 0),), file=sys.stderr)

    if check_summary.get("total", 0) > 0:
        print("  Violations: %s (C:%s H:%s M:%s L:%s)" % (
            check_summary.get('total', 0),
            check_summary.get('critical', 0),
            check_summary.get('high', 0),
            check_summary.get('medium', 0),
            check_summary.get('low', 0),
        ), file=sys.stderr)

    missing_acl = summary.get("security", {}).get("models_missing_acl", [])
    if missing_acl:
        print("  WARNING: %s model(s) missing ACL:" % (len(missing_acl),), file=sys.stderr)
        for m in missing_acl:
            print("    - %s" % (m,), file=sys.stderr)

    if args.format == "sari":
        check_results = results.get("check_results", {})
        violations = check_results.get("violations", [])
        from .sarif import violations_to_sarif
        sarif_doc = violations_to_sarif(violations)
        _write_output(json.dumps(sarif_doc, indent=2), args.output, "sari")
    elif args.format == "json" or args.format == "both":
        output = reporter.to_json()
        _write_output(output, args.output, "json")

    if args.format == "markdown" or args.format == "both" or args.format == "json":
        output = reporter.to_markdown() if not args.issues_only else reporter.to_markdown_issues()
        _write_output(output, args.output, "md")

    issues = results.get("issues", [])
    if issues:
        print("\n  Issues: %s found" % (len(issues),), file=sys.stderr)
        for i in issues:
            print("    [%s] %s" % (i['severity'], i['message'],), file=sys.stderr)

    return 0


def _write_output(content, output_path, ext):
    """Write content to file or stdout."""
    if output_path:
        base, _ = os.path.splitext(output_path)
        final_path = "%s.%s" % (base, ext,)
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Output written to: %s" % (final_path,), file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    sys.exit(main())
