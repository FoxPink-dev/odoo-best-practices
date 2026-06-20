class TestSARIF:
    def test_empty_violations(self):
        from analyzer.sarif import violations_to_sarif
        doc = violations_to_sarif([])
        assert doc["version"] == "2.1.0"
        assert len(doc["runs"]) == 1
        assert doc["runs"][0]["results"] == []

    def test_single_violation(self):
        from analyzer.sarif import violations_to_sarif
        violations = [
            {
                "rule": "orm-no-n-plus-1",
                "severity": "CRITICAL",
                "message": "search() inside loop",
                "file": "models/order.py",
                "line": 42,
                "confidence": 85,
            }
        ]
        doc = violations_to_sarif(violations)
        results = doc["runs"][0]["results"]
        assert len(results) == 1
        assert results[0]["ruleId"] == "orm-no-n-plus-1"
        assert results[0]["level"] == "error"

    def test_severity_mapping(self):
        from analyzer.sarif import violations_to_sarif, SEVERITY_TO_LEVEL
        assert SEVERITY_TO_LEVEL["CRITICAL"] == "error"
        assert SEVERITY_TO_LEVEL["HIGH"] == "error"
        assert SEVERITY_TO_LEVEL["MEDIUM"] == "warning"
        assert SEVERITY_TO_LEVEL["LOW"] == "note"

    def test_location(self):
        from analyzer.sarif import violations_to_sarif
        violations = [{"rule": "test", "severity": "HIGH", "message": "test",
                       "file": "test.py", "line": 10, "confidence": 50}]
        doc = violations_to_sarif(violations)
        loc = doc["runs"][0]["results"][0]["locations"][0]
        assert loc["physicalLocation"]["artifactLocation"]["uri"] == "test.py"
        assert loc["physicalLocation"]["region"]["startLine"] == 10

    def test_rule_metadata(self):
        from analyzer.sarif import violations_to_sarif
        violations = [{"rule": "orm-no-n-plus-1", "severity": "CRITICAL",
                       "message": "N+1 detected", "file": "f.py", "line": 1, "confidence": 85}]
        doc = violations_to_sarif(violations)
        rules = doc["runs"][0]["tool"]["driver"]["rules"]
        assert len(rules) >= 1
        rule = next(r for r in rules if r["id"] == "orm-no-n-plus-1")
        assert "shortDescription" in rule
        assert "fullDescription" in rule

    def test_unknown_rule_falls_back(self):
        from analyzer.sarif import violations_to_sarif
        violations = [{"rule": "nonexistent-rule", "severity": "LOW",
                       "message": "something", "file": "f.py", "line": 1, "confidence": 30}]
        doc = violations_to_sarif(violations)
        rules = doc["runs"][0]["tool"]["driver"]["rules"]
        assert any(r["id"] == "nonexistent-rule" for r in rules)

    def test_fix_suggestion_included(self):
        from analyzer.sarif import violations_to_sarif
        violations = [{"rule": "orm-no-n-plus-1", "severity": "CRITICAL",
                       "message": "N+1", "file": "f.py", "line": 1, "confidence": 85}]
        doc = violations_to_sarif(violations)
        result = doc["runs"][0]["results"][0]
        assert "fixSuggestion" in result

    def test_write_sarif(self):
        import tempfile, os
        from analyzer.sarif import write_sarif
        violations = [{"rule": "test", "severity": "LOW", "message": "test",
                       "file": "test.py", "line": 1, "confidence": 50}]
        with tempfile.NamedTemporaryFile(suffix=".sarif", delete=False, mode="w") as f:
            path = f.name
        try:
            result = write_sarif(violations, path)
            assert result == path
            assert os.path.isfile(path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)
