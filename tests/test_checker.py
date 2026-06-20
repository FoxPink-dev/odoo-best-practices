class TestCheckerACL:
    def test_detects_missing_acl(self, full_checker_results):
        models_with_acl = set()
        for v in full_checker_results["violations"]:
            if v["rule"] == "security-acl-required":
                models_with_acl.add(v.get("message", ""))
        demo_config_msgs = [m for m in models_with_acl if "demo.config" in m]
        assert len(demo_config_msgs) >= 1, "demo.config should not have ACL"

    def test_acl_critical_severity(self, full_checker_results):
        acl_violations = [v for v in full_checker_results["violations"]
                          if v["rule"] == "security-acl-required"]
        if acl_violations:
            assert all(v["severity"] == "CRITICAL" for v in acl_violations)

    def test_acl_confidence(self, full_checker_results):
        acl_violations = [v for v in full_checker_results["violations"]
                          if v["rule"] == "security-acl-required"]
        if acl_violations:
            assert all(v["confidence"] >= 90 for v in acl_violations)


class TestCheckerNplus1:
    def test_detects_search_in_loop(self, full_checker_results):
        n1_violations = [v for v in full_checker_results["violations"]
                         if v["rule"] == "orm-no-n-plus-1"]
        action_confirm = [v for v in n1_violations if "action_confirm" in v.get("message", "")]
        assert len(action_confirm) >= 1

    def test_n1_critical_severity(self, full_checker_results):
        n1_violations = [v for v in full_checker_results["violations"]
                         if v["rule"] == "orm-no-n-plus-1"]
        if n1_violations:
            assert all(v["severity"] == "CRITICAL" for v in n1_violations)


class TestCheckerRawSQL:
    def test_detects_raw_sql(self, full_checker_results):
        sql_violations = [v for v in full_checker_results["violations"]
                          if v["rule"] == "orm-raw-sql"]
        action_sql = [v for v in sql_violations if "action_sql_report" in v.get("message", "")]
        assert len(action_sql) >= 1

    def test_raw_sql_high_severity(self, full_checker_results):
        sql_violations = [v for v in full_checker_results["violations"]
                          if v["rule"] == "orm-raw-sql"]
        if sql_violations:
            assert all(v["severity"] == "HIGH" for v in sql_violations)

    def test_does_not_flag_search_read(self, full_checker_results):
        sql_violations = [v for v in full_checker_results["violations"]
                          if v["rule"] == "orm-raw-sql"]
        flagged_methods = [v.get("message", "") for v in sql_violations]
        assert not any("action_valid" in m or "action_no_issue" in m for m in flagged_methods)


class TestCheckerSudo:
    def test_detects_sudo(self, full_checker_results):
        sudo_violations = [v for v in full_checker_results["violations"]
                           if v["rule"] == "security-sudo-usage"]
        action_sudo = [v for v in sudo_violations if "action_sudo_method" in v.get("message", "")]
        assert len(action_sudo) >= 1

    def test_sudo_line_numbers(self, full_checker_results):
        sudo_violations = [v for v in full_checker_results["violations"]
                           if v["rule"] == "security-sudo-usage"]
        if sudo_violations:
            assert all(v.get("line", 0) > 0 for v in sudo_violations)


class TestCheckerSummary:
    def test_summary_has_total(self, full_checker_results):
        summary = full_checker_results["summary"]
        assert summary["total"] >= 3

    def test_summary_has_critical(self, full_checker_results):
        summary = full_checker_results["summary"]
        assert summary["critical"] >= 1

    def test_summary_has_high(self, full_checker_results):
        summary = full_checker_results["summary"]
        assert summary["high"] >= 1

    def test_summary_by_severity_matches(self, full_checker_results):
        summary = full_checker_results["summary"]
        total = sum(summary[k] for k in ("critical", "high", "medium", "low"))
        assert total == summary["total"]
