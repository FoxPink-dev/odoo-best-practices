# -*- coding: utf-8 -*-
"""
Unified data access layer for the Odoo Repository Intelligence platform.

RepositoryStore wraps the indexer, checker, graph, and knowledge base
into a single interface consumed by CLI, MCP, VS Code, and CI tools.

Usage:
    store = RepositoryStore('/path/to/addon')
    store.load()
    model = store.search_model('sale.order')
    violations = store.check_code()
    graph = store.inheritance_graph()
"""

import os
import json
from .indexer import RepositoryIndex
from .checker import Checker


# -- Knowledge base paths (domain model docs) --
_KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")


class RepositoryStore:
    """Unified data access layer over parsed Odoo addon data."""

    def __init__(self, addon_dir):
        self.addon_dir = os.path.abspath(addon_dir)
        self._index = None
        self._indexer = None
        self._check_results = None
        self._loaded = False

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self, reindex=False):
        """Parse the addon and build in-memory index + check results.

        Args:
            reindex: force re-parse even if already loaded.
        """
        if self._loaded and not reindex:
            return self

        # Build full index (this runs all parsers via Reporter internally)
        self._indexer = RepositoryIndex(self.addon_dir)
        self._index = self._indexer.build()
        self._total_models = len(self._index.get("models", []))
        self._total_fields = len(self._index.get("fields", []))

        # Run checker
        from .reporter import Reporter
        reporter = Reporter(self.addon_dir)
        all_results = reporter.run()
        self._check_results = all_results.get("check_results", {})
        self._all_results = all_results

        self._loaded = True
        return self

    def summary(self):
        """Return a one-line human-readable summary."""
        if not self._loaded:
            return "Store not loaded. Call .load() first."
        if self._indexer:
            return self._indexer.summary()
        return "Addon: {os.path.basename(self.addon_dir)} | {self._total_models} models"

    # ------------------------------------------------------------------
    # Model queries
    # ------------------------------------------------------------------

    def search_model(self, name):
        """Find a model by technical name."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.search_model(name)
        return None

    def list_models(self):
        """List all models in the repository."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.index.get("models", [])
        return []

    def fields_for_model(self, model_name):
        """Get all fields for a given model."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.fields_for_model(model_name)
        return []

    def methods_for_model(self, model_name):
        """Get all methods with decorators for a model."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.methods_for_model(model_name)
        return []

    def model_inheritance_chain(self, model_name, depth=10):
        """Resolve the full model inheritance chain (parent models)."""
        self._ensure_loaded()
        chain = []
        current = model_name
        visited = set()
        for _ in range(depth):
            if current in visited:
                break
            visited.add(current)
            model = self.search_model(current)
            if not model:
                break
            chain.append(current)
            inherits = model.get("inherit", [])
            if not inherits:
                break
            # Move to first parent that isn't self
            next_current = None
            for p in (inherits if isinstance(inherits, list) else [inherits]):
                if p != current:
                    next_current = p
                    break
            if not next_current:
                break
            current = next_current
        return chain

    def models_extending(self, model_name):
        """Find all models that inherit (extend) the given model.

        Returns list of model entries.
        """
        self._ensure_loaded()
        extending = []
        for m in self.list_models():
            inherit = m.get("inherit", [])
            if isinstance(inherit, list) and model_name in inherit:
                extending.append(m["tech_name"])
            elif inherit == model_name:
                extending.append(m["tech_name"])
        return sorted(extending)

    # ------------------------------------------------------------------
    # View queries
    # ------------------------------------------------------------------

    def search_view(self, view_id):
        """Find a view by XML ID."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.search_view(view_id)
        return None

    def list_views(self):
        """List all views in the repository."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.index.get("views", [])
        return []

    def view_inheritance_chain(self, view_id):
        """Resolve the full inheritance chain for a view."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.view_inheritance_chain(view_id)
        return []

    # ------------------------------------------------------------------
    # Action and menu queries
    # ------------------------------------------------------------------

    def search_action(self, action_id):
        """Find an action by XML ID."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.search_action(action_id)
        return None

    def list_actions(self):
        """List all actions in the repository."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.index.get("actions", [])
        return []

    def list_menus(self):
        """List all menus in the repository."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.index.get("menus", [])
        return []

    # ------------------------------------------------------------------
    # Security queries
    # ------------------------------------------------------------------

    def list_acls(self):
        """List all ACL entries."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.index.get("security", {}).get("acls", [])
        return []

    def list_record_rules(self):
        """List all record rules."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.index.get("security", {}).get("record_rules", [])
        return []

    def list_groups(self):
        """List all security groups."""
        self._ensure_loaded()
        if self._indexer:
            return self._indexer.index.get("security", {}).get("groups", [])
        return []

    def models_missing_acl(self):
        """Find models without ACL entries."""
        if not self._loaded:
            return []
        acl_models = set()
        for acl in self.list_acls():
            ref = acl.get("model_id", "")
            if ref and ref.startswith("model_"):
                acl_models.add(ref[6:].replace("_", "."))
        declared = {m["tech_name"] for m in self.list_models()}
        return list(declared - acl_models)

    def acls_for_model(self, model_name):
        """Get ACL entries for a specific model.

        Matches both 'model_<underscored_name>' XML-ID and direct name.
        """
        self._ensure_loaded()
        model_underscored = "model_" + model_name.replace(".", "_")
        result = []
        for acl in self.list_acls():
            ref = acl.get("model_id", "")
            if ref == model_underscored or ref == model_name:
                result.append(acl)
        return result

    def record_rules_for_model(self, model_name):
        """Get record rules for a specific model."""
        self._ensure_loaded()
        result = []
        for rule in self.list_record_rules():
            ref = rule.get("model_id", "")
            if ref == model_name or ref.endswith("." + model_name):
                result.append(rule)
        return result

    def model_dependencies(self):
        """Get the module dependency list from the manifest."""
        self._ensure_loaded()
        if self._all_results:
            return self._all_results.get("manifest", {}).get("depends", [])
        return []

    def menus_for_model(self, model_name):
        """Find menus that link to actions referencing this model."""
        self._ensure_loaded()
        action_ids = set()
        for a in self.list_actions():
            if a.get("res_model") == model_name:
                action_ids.add(a["id"])
        related = []
        for m in self.list_menus():
            action_ref = m.get("action", "")
            if action_ref in action_ids:
                related.append(m)
        return related

    # ------------------------------------------------------------------
    # Inheritance and dependency graphs
    # ------------------------------------------------------------------

    def inheritance_graph(self):
        """Return the model inheritance graph dict."""
        self._ensure_loaded()
        if self._all_results:
            return self._all_results.get("graph", {}).get("inheritance", {})
        return {}

    def dependency_graph(self):
        """Return the module dependency graph dict."""
        self._ensure_loaded()
        if self._all_results:
            return self._all_results.get("graph", {}).get("dependency", {})
        return {}

    def inheritance_graph_mermaid(self):
        """Return a Mermaid.js string of the inheritance graph."""
        self._ensure_loaded()
        if self._all_results:
            from .graph import graph_to_mermaid
            return graph_to_mermaid(self._all_results.get("graph", {}), "inheritance")
        return ""

    # ------------------------------------------------------------------
    # Code checking
    # ------------------------------------------------------------------

    def check_code(self):
        """Run the AST rule engine on the repository.

        Returns dict with 'violations' and 'summary'.
        """
        if self._check_results:
            return self._check_results
        return {"violations": [], "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}}

    def violations_by_severity(self, severity):
        """Filter violations by severity level.

        Args:
            severity: "CRITICAL", "HIGH", "MEDIUM", or "LOW"
        """
        results = self.check_code()
        return [v for v in results.get("violations", []) if v.get("severity") == severity.upper()]

    # ------------------------------------------------------------------
    # Domain knowledge
    # ------------------------------------------------------------------

    def explain_model(self, model_name):
        """Combine index data + knowledge base docs to explain a model.

        Returns a dict with structured info about the model.
        One call = ~80% model context.
        """
        self._ensure_loaded()
        model = self.search_model(model_name)
        if not model:
            return {"error": "Model '{model_name}' not found"}

        fields = self.fields_for_model(model_name)
        methods = self.methods_for_model(model_name)
        chain = self.model_inheritance_chain(model_name)
        extending = self.models_extending(model_name)
        knowledge_doc = self._load_knowledge(model_name)

        related_views = [
            v for v in self.list_views()
            if v.get("model") == model_name
        ]
        related_actions = [
            a for a in self.list_actions()
            if a.get("res_model") == model_name
        ]
        related_menus = self.menus_for_model(model_name)
        acl_entries = self.acls_for_model(model_name)
        rule_entries = self.record_rules_for_model(model_name)
        deps = self.model_dependencies()

        return {
            "model": model,
            "module": self._all_results.get("manifest", {}).get("name", ""),
            "fields_count": len(fields),
            "fields": fields[:30],
            "methods": methods,
            "inheritance": {
                "inherits": chain,
                "extended_by": extending,
            },
            "views": related_views,
            "actions": related_actions,
            "menus": related_menus,
            "acl": acl_entries,
            "record_rules": rule_entries,
            "dependencies": deps,
            "knowledge": knowledge_doc,
        }

    def list_knowledge_topics(self):
        """List available domain knowledge topics (model names)."""
        topics = []
        if not os.path.isdir(_KNOWLEDGE_DIR):
            return topics
        for fname in sorted(os.listdir(_KNOWLEDGE_DIR)):
            if fname.endswith(".md"):
                topics.append(fname.replace(".md", ""))
        return topics

    # ------------------------------------------------------------------
    # Full repository report
    # ------------------------------------------------------------------

    def repository_summary(self):
        """Return a full summary dict of the entire repository."""
        self._ensure_loaded()
        if self._all_results:
            return self._all_results.get("summary", {})

        models = self.list_models()
        fields = self._index.get("fields", [])
        views = self.list_views()
        actions = self.list_actions()
        menus = self._index.get("menus", [])
        acls = self.list_acls()
        violations = self.check_code()

        return {
            "addon": os.path.basename(self.addon_dir),
            "models": len(models),
            "fields": len(fields),
            "views": len(views),
            "actions": len(actions),
            "menus": len(menus),
            "acls": len(acls),
            "violations": violations.get("summary", {}).get("total", 0),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ensure_loaded(self):
        if not self._loaded:
            raise RuntimeError("RepositoryStore not loaded. Call .load() first.")

    def _load_knowledge(self, topic):
        """Load a knowledge base markdown file for a given topic."""
        for ext in (".md", ".txt"):
            fpath = os.path.join(_KNOWLEDGE_DIR, topic + ext)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        return f.read()
                except IOError:
                    return None
        return None
