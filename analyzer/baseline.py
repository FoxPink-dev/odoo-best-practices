# -*- coding: utf-8 -*-
"""
Baseline / Suppression system for Odoo checker.

Allows onboarding legacy repositories by generating a baseline of known
violations. After baseline, only NEW violations are reported.

Usage:
    from analyzer.baseline import Baseline

    bl = Baseline("/path/to/addon")
    bl.generate()           # Create baseline from current violations
    bl.filter(violations)   # Remove known violations, return only new ones

File format (baseline.json):
    {
        "version": 1,
        "addon": "my_addon",
        "timestamp": "2026-06-20T12:00:00Z",
        "total_accepted": 387,
        "accepted": [
            {"rule": "orm-no-n-plus-1", "file": "models/foo.py", "line": 54},
            ...
        ]
    }
"""

import json
import os
from datetime import datetime, timezone


BASELINE_FILENAME = "odoo-baseline.json"
BASELINE_VERSION = 1


def _violation_key(v):
    """Generate a unique key for a violation (rule + file + line).

    Used for matching against baseline entries.
    """
    return (v.get("rule", ""), v.get("file", ""), v.get("line", 0))


class Baseline:
    """Manage known violations for suppression during code review.

    Typical workflow for legacy repositories:
        1. Generate baseline:   baseline = Baseline(addon_dir); baseline.generate()
        2. Subsequent checks:   new = baseline.filter(current_violations)
    """

    def __init__(self, addon_dir, baseline_path=None):
        self.addon_dir = os.path.abspath(addon_dir)
        self.addon_name = os.path.basename(self.addon_dir)
        self._baseline_path = baseline_path or os.path.join(
            self.addon_dir, BASELINE_FILENAME
        )
        self._baseline_data = None

    # ------------------------------------------------------------------
    # Generate baseline from current checker violations
    # ------------------------------------------------------------------

    def generate(self, violations=None):
        """Generate a baseline from the given violations.

        If violations is None, runs the checker to collect them.

        Returns the baseline dict and writes it to baseline.json in addon_dir.
        """
        if violations is None:
            from .store import RepositoryStore
            store = RepositoryStore(self.addon_dir)
            store.load()
            violations = store.check_code().get("violations", [])

        accepted = []
        seen = set()

        for v in violations:
            key = _violation_key(v)
            if key not in seen:
                seen.add(key)
                entry = {
                    "rule": v.get("rule", "unknown"),
                    "file": v.get("file", ""),
                    "line": v.get("line", 1),
                }
                accepted.append(entry)

        self._baseline_data = {
            "version": BASELINE_VERSION,
            "addon": self.addon_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_accepted": len(accepted),
            "accepted": accepted,
        }

        self._write()
        return self._baseline_data

    # ------------------------------------------------------------------
    # Load baseline from file
    # ------------------------------------------------------------------

    def load(self):
        """Load baseline from disk. Returns False if not found."""
        if not os.path.isfile(self._baseline_path):
            return False

        try:
            with open(self._baseline_path, "r", encoding="utf-8") as f:
                self._baseline_data = json.load(f)
            return True
        except (IOError, json.JSONDecodeError):
            return False

    # ------------------------------------------------------------------
    # Filter violations against baseline
    # ------------------------------------------------------------------

    def filter(self, violations):
        """Separate violations into known (baseline) and new.

        Args:
            violations: Full list of violation dicts from Checker.

        Returns:
            dict with:
                "new":    list — violations not in baseline
                "known":  list — violations matched by baseline
                "summary": {
                    "total": len(violations),
                    "known": len(matched),
                    "new":   len(new_list),
                }
        """
        if not self._baseline_data:
            return {"new": violations, "known": [], "summary": {
                "total": len(violations), "known": 0, "new": len(violations)
            }}

        baseline_keys = set()
        for entry in self._baseline_data.get("accepted", []):
            key = (entry.get("rule", ""), entry.get("file", ""), entry.get("line", 0))
            baseline_keys.add(key)

        new_list = []
        known_list = []

        for v in violations:
            key = _violation_key(v)
            if key in baseline_keys:
                known_list.append(v)
            else:
                new_list.append(v)

        return {
            "new": new_list,
            "known": known_list,
            "summary": {
                "total": len(violations),
                "known": len(known_list),
                "new": len(new_list),
            },
        }

    # ------------------------------------------------------------------
    # Stats / status
    # ------------------------------------------------------------------

    def stats(self):
        """Return human-readable baseline status."""
        if not self._baseline_data:
            return "No baseline loaded."

        total = self._baseline_data.get("total_accepted", 0)
        timestamp = self._baseline_data.get("timestamp", "?")
        return "Baseline: %s accepted violations (from %s)" % (total, timestamp)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _write(self):
        """Write baseline to disk."""
        with open(self._baseline_path, "w", encoding="utf-8") as f:
            json.dump(self._baseline_data, f, indent=2)
