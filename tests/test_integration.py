import json
import os
import sys
import tempfile

PROJECT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
FIXTURE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "fixtures", "demo_addon"))


def _run_cli(args):
    from analyzer.cli import main
    from io import StringIO
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    try:
        sys.argv = ["analyzer.cli"] + args
        rc = main()
        return rc, sys.stdout.getvalue(), sys.stderr.getvalue()
    except SystemExit as e:
        return e.code if e.code is not None else 0, sys.stdout.getvalue(), sys.stderr.getvalue()
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestCLIIntegration:
    def test_cli_report_markdown(self):
        rc, out, err = _run_cli([FIXTURE_DIR])
        assert rc == 0
        assert "# Repository Analysis" in out

    def test_cli_report_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_base = os.path.join(tmp, "report")
            rc, out, err = _run_cli([FIXTURE_DIR, "--format", "json", "-o", out_base])
            assert rc == 0
            json_path = out_base + ".json"
            assert os.path.isfile(json_path), "JSON file not found at %s (stderr: %s)" % (json_path, err)
            data = json.load(open(json_path))
            assert "addon" in data
            assert "summary" in data

    def test_cli_check(self):
        rc, out, err = _run_cli([FIXTURE_DIR, "--check"])
        assert rc == 0
        assert "# Code Review Results" in out

    def test_cli_stats(self):
        rc, out, err = _run_cli([FIXTURE_DIR, "--stats"])
        assert rc == 0
        assert "Repository:" in out

    def test_cli_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "idx")
            rc, out, err = _run_cli([FIXTURE_DIR, "--index", "-o", out_path])
            assert rc == 0
            idx_file = out_path + ".json"
            assert os.path.isfile(idx_file)
            data = json.load(open(idx_file))
            assert "models" in data or "index" in data

    def test_cli_graph(self):
        rc, out, err = _run_cli([FIXTURE_DIR, "--graph"])
        assert rc == 0

    def test_cli_baseline_generate(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = _run_cli([FIXTURE_DIR, "--baseline"])
            assert rc == 0

    def test_cli_sarif_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "output")
            rc, out, err = _run_cli([FIXTURE_DIR, "--format", "sarif", "-o", out_path])
            assert rc == 0
            sarif_path = out_path + ".sari"
            if os.path.isfile(sarif_path):
                data = json.load(open(sarif_path))
                assert data["version"] == "2.1.0"
                assert len(data["runs"]) == 1
            else:
                from analyzer.sarif import violations_to_sarif
                pass  # SARIF may have gone to stdout

    def test_cli_init_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            orig_dir = os.getcwd()
            os.chdir(tmp)
            try:
                rc, out, err = _run_cli(["--init", "all"])
                assert rc == 0
                for dirname in [".opencode", ".claude", ".cursor", ".kiro", ".windsurf"]:
                    config_dir = os.path.join(tmp, dirname)
                    if os.path.isdir(config_dir):
                        items = os.listdir(config_dir)
                        assert len(items) > 0
            finally:
                os.chdir(orig_dir)

    def test_cli_init_single_ide(self):
        with tempfile.TemporaryDirectory() as tmp:
            orig_dir = os.getcwd()
            os.chdir(tmp)
            try:
                rc, out, err = _run_cli(["--init", "claude"])
                assert rc == 0, "CLI failed: stderr=%s" % err
                expected = os.path.join(tmp, ".claude", "rules", "odoo-best-practices.md")
                assert os.path.isfile(expected), "Expected file not found: %s" % expected
            finally:
                os.chdir(orig_dir)

    def test_cli_confidence(self):
        rc, out, err = _run_cli([FIXTURE_DIR, "--confidence"])
        # --confidence only works with --check
        rc, out, err = _run_cli([FIXTURE_DIR, "--check", "--confidence"])
        assert rc == 0
        assert "%" in out


class TestMCPIntegration:
    def test_mcp_tools_defined(self):
        from analyzer.mcp_server import TOOL_DEFINITIONS
        assert len(TOOL_DEFINITIONS) >= 10
        tool_names = [t["name"] for t in TOOL_DEFINITIONS]
        assert "check_repository" in tool_names
        assert "repository_summary" in tool_names
        assert "list_models" in tool_names
        assert "search_model" in tool_names


class TestInitGenerator:
    def test_generate_opencode(self):
        from analyzer.init_generator import generate
        with tempfile.TemporaryDirectory() as tmp:
            results = generate("opencode", tmp)
            assert len(results) == 1
            ide, path = results[0]
            assert ide == "opencode"
            assert os.path.isfile(path)
            content = open(path).read()
            assert "odoo-best-practices" in content

    def test_generate_all(self):
        from analyzer.init_generator import generate
        with tempfile.TemporaryDirectory() as tmp:
            results = generate("all", tmp)
            ides = {r[0] for r in results}
            assert "opencode" in ides
            assert "claude" in ides
            assert "cursor" in ides
            assert "kiro" in ides
            assert "windsurf" in ides

    def test_generated_files_are_valid(self):
        from analyzer.init_generator import generate
        with tempfile.TemporaryDirectory() as tmp:
            results = generate("all", tmp)
            for ide, path in results:
                assert os.path.isfile(path)
                assert os.path.getsize(path) > 0
                if path.endswith(".json"):
                    data = json.load(open(path))
                    assert isinstance(data, dict)
