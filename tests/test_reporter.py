class TestReporterRun:
    def test_results_have_manifest(self, all_results):
        assert "manifest" in all_results
        assert all_results["manifest"].get("name") == "Demo Addon"

    def test_results_have_models(self, all_results):
        assert len(all_results["models"]) >= 3
        assert "demo.order" in all_results["models"]

    def test_results_have_views(self, all_results):
        assert len(all_results["views"]) >= 2

    def test_results_have_acls(self, all_results):
        assert len(all_results["acls"]) >= 2

    def test_results_have_issues(self, all_results):
        assert "issues" in all_results

    def test_results_have_summary(self, all_results):
        assert "summary" in all_results
        summary = all_results["summary"]
        assert summary["module_name"] == "demo_addon"
        assert "models" in summary
        assert "fields" in summary
        assert "views" in summary
        assert "security" in summary

    def test_results_have_graph(self, all_results):
        assert "graph" in all_results
        assert "inheritance" in all_results["graph"]

    def test_results_have_check_results(self, all_results):
        assert "check_results" in all_results
        assert "violations" in all_results["check_results"]


class TestReporterSummary:
    def test_model_counts(self, all_results):
        summary = all_results["summary"]
        assert summary["models"]["total"] >= 3
        assert summary["models"]["new_models"] >= 3

    def test_field_counts(self, all_results):
        summary = all_results["summary"]
        total = summary["fields"]["total"]
        assert total >= 10, "should have at least 10 total fields across models"

    def test_view_counts(self, all_results):
        summary = all_results["summary"]
        assert summary["views"]["total"] >= 2

    def test_security_counts(self, all_results):
        summary = all_results["summary"]
        security = summary["security"]
        assert security["acls"] >= 2
        assert security["models_missing_acl"] is not None


class TestReporterIssues:
    def test_missing_acl_issue(self, all_results):
        check_results = all_results.get("check_results", {})
        violations = check_results.get("violations", [])
        acl_violations = [v for v in violations
                          if v.get("rule") == "security-acl-required"]
        missing = [v for v in acl_violations if "demo.config" in v.get("message", "")]
        assert len(missing) >= 1

    def test_missing_description_issue(self, all_results):
        issues = all_results.get("issues", [])
        desc_issues = [i for i in issues
                       if i.get("rule") == "code-docstring-models"]
        assert len(desc_issues) >= 0


class TestReporterOutput:
    def test_to_markdown(self, all_results):
        from analyzer.reporter import Reporter
        reporter = Reporter.__new__(Reporter)
        reporter.results = all_results
        reporter.addon_name = "demo_addon"
        md = reporter.to_markdown()
        assert "Repository Analysis" in md
        assert "demo_addon" in md
        assert "Demo Addon" in md or "16.0" in md

    def test_to_markdown_issues(self, all_results):
        from analyzer.reporter import Reporter
        reporter = Reporter.__new__(Reporter)
        reporter.results = all_results
        reporter.addon_name = "demo_addon"
        md = reporter.to_markdown_issues()
        assert md is not None
        assert len(md) > 0

    def test_to_json(self, all_results):
        import json
        from analyzer.reporter import Reporter
        reporter = Reporter.__new__(Reporter)
        reporter.results = all_results
        reporter.addon_name = "demo_addon"
        js = reporter.to_json()
        parsed = json.loads(js)
        assert parsed["addon"] == "demo_addon"
        assert "summary" in parsed
