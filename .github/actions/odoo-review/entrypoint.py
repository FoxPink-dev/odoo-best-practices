"""
Odoo Review — GitHub Action entrypoint.

Runs static analysis on the addon, posts a PR comment with violations,
and exits with failure if violations exceed the configured thresholds.

Usage (from Docker):
    python entrypoint.py <addon-path> <fail-on-critical> <fail-on-high>

Environment:
    GITHUB_TOKEN     — GitHub API token for PR comments
    GITHUB_REPOSITORY — e.g. "owner/repo"
    GITHUB_PR_NUMBER  — PR number (set by actions/checkout + workflow context)
"""

import json
import os
import sys
import urllib.request
import urllib.parse

# Add the analyzer package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer.store import RepositoryStore
from analyzer.sarif import violations_to_sarif, write_sarif
from analyzer.baseline import Baseline


# ------------------------------------------------------------------
# GitHub API helpers
# ------------------------------------------------------------------

def post_pr_comment(token, repo, pr_number, body):
    """Post a comment on a GitHub PR."""
    if not token or not repo or not pr_number:
        return False
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    data = json.dumps({"body": body}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req)
        return resp.status == 201
    except Exception as e:
        print(f"::warning::Failed to post PR comment: {e}", file=sys.stderr)
        return False


def format_violations(violations):
    """Format violations as a GitHub-flavored markdown report."""
    by_severity = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
    for v in violations:
        sev = v.get("severity", "LOW").upper()
        by_severity.setdefault(sev, []).append(v)

    lines = []
    lines.append("## Odoo Analysis Report\n")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")

    sev_icons = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "⚪"}
    total = 0
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        cnt = len(by_severity.get(sev, []))
        if cnt:
            icon = sev_icons.get(sev, "")
            lines.append(f"| {icon} **{sev}** | {cnt} |")
            total += cnt
    lines.append(f"| **Total** | **{total}** |")
    lines.append("")

    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        items = by_severity.get(sev, [])
        if not items:
            continue
        icon = sev_icons.get(sev, "")
        lines.append(f"### {icon} {sev} ({len(items)})")
        lines.append("")
        for v in items:
            file = v.get("file", "?")
            line_num = v.get("line", "?")
            rule = v.get("rule", "?")
            message = v.get("message", "?")
            lines.append(f"- **`{file}:{line_num}`** — {message}")
            lines.append(f"  <sub>rule: `{rule}`</sub>")
        lines.append("")

    if total == 0:
        lines.append("✅ No violations found.\n")

    return "\n".join(lines)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    addon_path = sys.argv[1] if len(sys.argv) > 1 else "."
    fail_on_critical = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True
    fail_on_high = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True
    generate_baseline = sys.argv[4].lower() == "true" if len(sys.argv) > 4 else False
    baseline_path = sys.argv[5] if len(sys.argv) > 5 else ""
    use_baseline = sys.argv[6].lower() == "true" if len(sys.argv) > 6 else False

    github_token = os.environ.get("GITHUB_TOKEN", "")
    github_repo = os.environ.get("GITHUB_REPOSITORY", "")
    pr_number = os.environ.get("GITHUB_PR_NUMBER", "")

    # Resolve addon path
    workspace = os.environ.get("GITHUB_WORKSPACE", ".")
    abs_addon = os.path.join(workspace, addon_path)
    baseline_path = os.path.join(abs_addon, baseline_path) if baseline_path else os.path.join(abs_addon, "odoo-baseline.json")

    print(f"::group::Odoo Review — {addon_path}")
    print(f"Analyzing: {abs_addon}")

    if not os.path.isdir(abs_addon):
        print(f"::error::Addon directory not found: {abs_addon}")
        sys.exit(1)

    # Load baseline if requested
    violations_list = []
    known_count = 0
    summary = {"models": 0, "fields": 0, "violations": 0}
    v_summary = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}

    if generate_baseline:
        from analyzer.baseline import Baseline
        print(f"::group::Generating baseline")
        bl = Baseline(abs_addon, baseline_path=baseline_path)
        baseline = bl.generate()
        print(f"::endgroup::")
    else:
        # Run analysis
        store = RepositoryStore(abs_addon)
        store.load()

        summary = store.repository_summary()
        violations = store.check_code()
        violations_list = violations.get("violations", [])
        v_summary = violations.get("summary", {})

        # Apply baseline suppression if requested
        if use_baseline:
            from analyzer.baseline import Baseline
            bl = Baseline(abs_addon, baseline_path=baseline_path)
            loaded = bl.load()
            if loaded:
                filtered = bl.filter(violations_list)
                violations_list = filtered["new"]
                known_count = filtered["summary"]["known"]
                print(f"::group::Baseline suppression applied: {known_count} known violations suppressed")
                print(f"::endgroup::")
            else:
                print(f"::group::Warning: no baseline found at {baseline_path}")
                print(f"::endgroup::")

        print(f"Models: {summary.get('models', 0)}")
        print(f"Fields: {summary.get('fields', 0)}")
        print(f"Violations: {v_summary.get('total', 0)}")
        if known_count:
            print(f"Known (suppressed): {known_count}")
        print(f"  CRITICAL: {v_summary.get('critical', 0)}")
        print(f"  HIGH: {v_summary.get('high', 0)}")
    # Output GitHub annotations for each violation (NEW violations only)
    if violations_list:
        for v in violations_list:
            file = v.get("file", "")
            line = v.get("line", 1)
            sev = v.get("severity", "LOW").upper()
            msg = v.get("message", "")
            rule = v.get("rule", "")
            annotation_level = "error" if sev in ("CRITICAL", "HIGH") else "warning"
            print(f"::{annotation_level} file={file},line={line},title={sev}: {rule}::{msg}")

    # Post PR comment (skip during baseline generation)
    if not generate_baseline:
        report = format_violations(violations_list)
        post_pr_comment(github_token, github_repo, pr_number, report)

    # Write SARIF output for GitHub Code Scanning
    sarif_path = os.path.join(workspace, "odoo-review-results.sarif")
    try:
        write_sarif(violations_list, sarif_path)
        print(f"SARIF output: {sarif_path}")
    except Exception as e:
        print(f"::warning::Failed to write SARIF: {e}")

    print("::endgroup::")

    # Determine exit code based on NEW violations only
    critical_count = v_summary.get("critical", 0)
    high_count = v_summary.get("high", 0)

    should_fail = False
    if fail_on_critical and critical_count > 0:
        print("::error::CRITICAL violations found. Failing.")
        should_fail = True
    if fail_on_high and high_count > 0:
        print("::error::HIGH violations found. Failing.")
        should_fail = True

    if should_fail:
        sys.exit(1)
    else:
        print("✅ Analysis passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
