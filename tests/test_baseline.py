import json
import os
import tempfile


class TestBaseline:
    def test_generate_accepts_violations(self, tmp_path):
        from analyzer.baseline import Baseline
        violations = [
            {"rule": "orm-no-n-plus-1", "file": "models/foo.py", "line": 42},
            {"rule": "orm-raw-sql", "file": "models/foo.py", "line": 100},
        ]
        repo = tmp_path / "fake_addon"
        repo.mkdir()
        bl = Baseline(str(repo))
        baseline = bl.generate(violations)
        assert baseline["total_accepted"] == 2
        assert len(baseline["accepted"]) == 2

    def test_load_returns_false_if_missing(self):
        from analyzer.baseline import Baseline
        bl = Baseline(str(self._tmp_dir()))
        loaded = bl.load()
        assert loaded is False

    def test_load_and_filter(self, tmp_path):
        from analyzer.baseline import Baseline
        baseline_file = tmp_path / "baseline.json"
        baseline_file.write_text(json.dumps({
            "version": 1,
            "addon": "test",
            "timestamp": "2026-01-01T00:00:00",
            "total_accepted": 1,
            "accepted": [{"rule": "orm-no-n-plus-1", "file": "test.py", "line": 5}],
        }))
        bl = Baseline(str(tmp_path), baseline_path=str(baseline_file))
        assert bl.load() is True
        current = [
            {"rule": "orm-no-n-plus-1", "file": "test.py", "line": 5},
            {"rule": "orm-raw-sql", "file": "test.py", "line": 10},
        ]
        result = bl.filter(current)
        assert len(result["known"]) == 1
        assert len(result["new"]) == 1
        assert result["summary"]["total"] == 2
        assert result["summary"]["known"] == 1
        assert result["summary"]["new"] == 1

    def test_filter_without_load(self, tmp_path):
        from analyzer.baseline import Baseline
        bl = Baseline(str(tmp_path))
        current = [{"rule": "test", "file": "a.py", "line": 1}]
        result = bl.filter(current)
        assert result["summary"]["new"] == 1
        assert result["summary"]["known"] == 0

    def test_filter_deduplicates(self, tmp_path):
        from analyzer.baseline import Baseline
        baseline_file = tmp_path / "baseline.json"
        baseline_file.write_text(json.dumps({
            "version": 1,
            "addon": "test",
            "timestamp": "2026-06-20T00:00:00",
            "total_accepted": 1,
            "accepted": [{"rule": "duplicate", "file": "dup.py", "line": 1}],
        }))
        bl = Baseline(str(tmp_path), baseline_path=str(baseline_file))
        bl.load()
        violations = [
            {"rule": "duplicate", "file": "dup.py", "line": 1},
            {"rule": "new", "file": "new.py", "line": 10},
        ]
        result = bl.filter(violations)
        assert len(result["known"]) == 1
        assert len(result["new"]) == 1

    def test_stats_without_data(self, tmp_path):
        from analyzer.baseline import Baseline
        bl = Baseline(str(tmp_path))
        stats = bl.stats()
        assert "No baseline" in stats

    def test_stats_with_data(self, tmp_path):
        from analyzer.baseline import Baseline
        bl = Baseline(str(tmp_path))
        bl._baseline_data = {"total_accepted": 10, "timestamp": "2026-01-01"}
        stats = bl.stats()
        assert "10" in stats

    @staticmethod
    def _tmp_dir():
        import tempfile
        return tempfile.mkdtemp()
