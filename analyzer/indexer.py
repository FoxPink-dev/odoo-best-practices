# -*- coding: utf-8 -*-
"""
Phase 7.5 — Repository Index (pseudo-MCP).

Generates a searchable repository_index.json from parsed addon data.
AI can query this index without connecting to a live Odoo instance.

Key search functions:
  search_model(name)    → model definition + fields + methods
  search_view(name)     → view definition + inheritance chain
  search_field(model)   → all fields for a model
  search_action(name)   → action definition
  search_menu(name)     → menu location
  search_model_method(name) → method with decorators
"""

import json
import os
from .reporter import Reporter


class RepositoryIndex:
    """Build a flat, searchable index from parsed Odoo addon data."""

    def __init__(self, addon_dir):
        self.addon_dir = os.path.abspath(addon_dir)
        self.reporter = Reporter(self.addon_dir)
        self.index = {
            "addon": os.path.basename(self.addon_dir),
            "path": self.addon_dir,
            "version": None,
            "models": [],
            "fields": [],
            "views": [],
            "actions": [],
            "menus": [],
            "templates": [],
            "security": {
                "acls": [],
                "record_rules": [],
                "groups": [],
            },
            "_search": {},  # name → entry lookup
        }

    def build(self):
        """Run parser and index all artifacts."""
        results = self.reporter.run()
        self.index["version"] = results["manifest"].get("version", "unknown")

        # Index models
        for tech_name, info in results["models"].items():
            entry = {
                "type": "model",
                "tech_name": tech_name,
                "class_name": info["class_name"],
                "file": info["file"],
                "line": info.get("line"),
                "description": info.get("_description"),
                "inherit": info.get("_inherit", []),
                "inherits": list(info.get("_inherits", {}).keys()) if info.get("_inherits") else [],
                "has_name": bool(info.get("_name")),
                "is_extension": not bool(info.get("_name")) and bool(info.get("_inherit")),
                "fields": [],
                "methods": [],
            }

            # Index fields for this model
            for field in results["fields"].get(tech_name, []):
                field_entry = {
                    "type": "field",
                    "name": field["name"],
                    "field_type": field.get("type"),
                    "model": tech_name,
                    "file": info["file"],
                    "line": field.get("line"),
                    "params": field.get("params", {}),
                }
                self.index["fields"].append(field_entry)
                entry["fields"].append(field["name"])

            # Index methods for this model
            for method in results["methods"].get(tech_name, []):
                method_entry = {
                    "type": "method",
                    "name": method["name"],
                    "model": tech_name,
                    "line": method.get("line"),
                    "decorators": method.get("decorators", []),
                }
                entry["methods"].append(method_entry)

            self.index["models"].append(entry)

        # Index views
        for view in results["views"]:
            entry = {
                "type": "view",
                "id": view["id"],
                "name": view["name"],
                "model": view["model"],
                "view_type": view["type"],
                "inherit_id": view.get("inherit_id"),
                "priority": view.get("priority"),
                "file": view["file"],
            }
            self.index["views"].append(entry)

        # Index actions
        for action in results["actions"]:
            entry = {
                "type": "action",
                "id": action["id"],
                "name": action["name"],
                "action_type": action["model"].replace("ir.actions.", ""),
                "res_model": action.get("res_model"),
                "view_mode": action.get("view_mode"),
                "file": action["file"],
            }
            self.index["actions"].append(entry)

        # Index menus
        for menu in results["menus"]:
            entry = {
                "type": "menu",
                "id": menu["id"],
                "name": menu["name"],
                "parent": menu.get("parent"),
                "action": menu.get("action"),
                "sequence": menu.get("sequence"),
                "file": menu["file"],
            }
            self.index["menus"].append(entry)

        # Index templates (QWeb)
        for tmpl in results["templates"]:
            entry = {
                "type": "template",
                "id": tmpl["id"],
                "name": tmpl.get("name"),
                "inherit_id": tmpl.get("inherit_id"),
                "file": tmpl["file"],
            }
            self.index["templates"].append(entry)

        # Index security
        self.index["security"]["acls"] = results["acls"]
        self.index["security"]["record_rules"] = results["record_rules"]
        self.index["security"]["groups"] = results["groups"]

        # Build name lookup
        self._build_search_index()

        return self.index

    def _build_search_index(self):
        """Build a flat name-to-entry lookup for fast searching."""
        search = {}
        for entry in self.index["models"]:
            search[entry["tech_name"]] = entry
            search["model:%s" % entry['tech_name']] = entry
        for entry in self.index["views"]:
            search[entry["id"]] = entry
            search["view:%s" % entry['id']] = entry
        for entry in self.index["actions"]:
            search[entry["id"]] = entry
            search["action:%s" % entry['id']] = entry
        for entry in self.index["menus"]:
            search[entry["id"]] = entry
            search["menu:%s" % entry['id']] = entry
        for entry in self.index["fields"]:
            search["field:%s.%s" % (entry['model'], entry['name'])] = entry
        self.index["_search"] = search

    # --- Query API (usable by AI as pseudo-MCP) ---

    def search_model(self, name):
        """Find a model by technical name. Returns entry or None."""
        return self._find("model", "tech_name", name)

    def search_view(self, view_id):
        """Find a view by XML ID. Returns entry or None."""
        return self._find("view", "id", view_id)

    def search_action(self, action_id):
        """Find an action by XML ID. Returns entry or None."""
        return self._find("action", "id", action_id)

    def search_menu(self, menu_id):
        """Find a menu by XML ID. Returns entry or None."""
        return self._find("menu", "id", menu_id)

    def fields_for_model(self, model_name):
        """Get all fields for a given model."""
        return [f for f in self.index["fields"] if f["model"] == model_name]

    def methods_for_model(self, model_name):
        """Get all methods with decorators for a model."""
        model = self.search_model(model_name)
        return model.get("methods", []) if model else []

    def view_inheritance_chain(self, view_id):
        """Resolve the full inheritance chain for a view."""
        chain = []
        current_id = view_id
        visited = set()
        while current_id and current_id not in visited:
            visited.add(current_id)
            chain.append(current_id)
            view = self.search_view(current_id)
            if view and view.get("inherit_id"):
                # Handle ref format: module.view_id
                inherit_ref = view["inherit_id"]
                if "." in inherit_ref:
                    current_id = inherit_ref.split(".", 1)[1]
                else:
                    current_id = inherit_ref
            else:
                current_id = None
        return chain

    def model_inheritance_chain(self, model_name, depth=10):
        """Resolve the full model inheritance chain (up to depth)."""
        chain = []
        current = model_name
        for _ in range(depth):
            model = self.search_model(current)
            if not model:
                break
            chain.append(current)
            inherits = model.get("inherit", [])
            if inherits:
                current = inherits[0]  # First parent
            else:
                break
        return chain

    def to_json(self, indent=2):
        """Serialize index to JSON."""
        def _serialize(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError("Type %s not serializable" % type(obj))

        # Remove internal search index from output
        output = {k: v for k, v in self.index.items() if k != "_search"}
        return json.dumps(output, indent=indent, default=_serialize)

    def _find(self, category, key, value):
        """Find an entry in a category by key-value match."""
        for entry in self.index.get("%ss" % category, []):
            if entry.get(key) == value:
                return entry
        return None

    def summary(self):
        """Return a one-line summary of the repository."""
        return (
            "Repository: %s v%s | "
            "%s models, %s fields, %s views, %s actions, %s menus, %s ACLs"
        ) % (
            self.index['addon'],
            self.index['version'],
            len(self.index['models']),
            len(self.index['fields']),
            len(self.index['views']),
            len(self.index['actions']),
            len(self.index['menus']),
            len(self.index['security']['acls']),
        )


def build_index(addon_dir, output_path=None):
    """Convenience function: build index and optionally write to file."""
    indexer = RepositoryIndex(addon_dir)
    index = indexer.build()

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(indexer.to_json())

    return indexer
