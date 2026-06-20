# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET


class ViewParser:
    """Parse Odoo XML files to extract views, actions, menus, templates."""

    def __init__(self):
        self.views = []          # [ViewInfo]
        self.actions = []        # [ActionInfo]
        self.menus = []          # [MenuInfo]
        self.templates = []      # [TemplateInfo]

    def parse_addon(self, addon_dir):
        """Recursively parse all XML files in an addon directory."""
        for root, dirs, files in os.walk(addon_dir):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "migrations", "static")]
            for fname in files:
                if fname.endswith(".xml"):
                    filepath = os.path.join(root, fname)
                    self._parse_xml_file(filepath, addon_dir)

    def _parse_xml_file(self, filepath, addon_dir):
        """Parse a single XML data file for Odoo views/actions/menus."""
        rel_path = os.path.relpath(filepath, addon_dir).replace("\\", "/")
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except (ET.ParseError, IOError):
            return

        for record in root.iter("record"):
            model = record.get("model", "")
            record_id = record.get("id", "")

            if model == "ir.ui.view":
                self._parse_view_record(record, record_id, rel_path)
            elif model in ("ir.actions.act_window", "ir.actions.server",
                           "ir.actions.client", "ir.actions.report",
                           "ir.actions.url"):
                self.actions.append(self._parse_action_record(record, record_id, model, rel_path))
            elif model == "ir.ui.menu":
                self.menus.append(self._parse_menu_record(record, record_id, rel_path))

        for template in root.iter("template"):
            self.templates.append({
                "id": template.get("id", ""),
                "name": template.get("name", ""),
                "inherit_id": template.get("inherit_id", ""),
                "priority": template.get("priority", "16"),
                "file": rel_path,
            })

        for menuitem in root.iter("menuitem"):
            self.menus.append({
                "id": menuitem.get("id", ""),
                "name": menuitem.get("name", ""),
                "parent": menuitem.get("parent", ""),
                "action": menuitem.get("action", ""),
                "sequence": menuitem.get("sequence", "10"),
                "groups": menuitem.get("groups", ""),
                "file": rel_path,
            })

    def _parse_view_record(self, record, record_id, rel_path):
        """Parse a ir.ui.view record for view metadata."""
        fields = self._record_fields(record)
        inherit_id = fields.get("inherit_id", {})
        inherit_ref = inherit_id.get("re", "") if isinstance(inherit_id, dict) else ""

        arch = fields.get("arch", "")
        view_type = self._detect_view_type(arch, fields)

        self.views.append({
            "id": record_id,
            "name": fields.get("name", record_id),
            "model": fields.get("model", ""),
            "type": view_type,
            "inherit_id": inherit_ref,
            "priority": fields.get("priority", "16"),
            "groups": fields.get("groups", ""),
            "active": fields.get("active", "True"),
            "file": rel_path,
        })

    def _parse_action_record(self, record, record_id, model, rel_path):
        """Parse an action record."""
        fields = self._record_fields(record)
        return {
            "id": record_id,
            "name": fields.get("name", record_id),
            "model": model,
            "res_model": fields.get("res_model", ""),
            "view_mode": fields.get("view_mode", ""),
            "domain": fields.get("domain", ""),
            "context": fields.get("context", ""),
            "target": fields.get("target", "current"),
            "binding_model_id": fields.get("binding_model_id", ""),
            "file": rel_path,
        }

    def _parse_menu_record(self, record, record_id, rel_path):
        """Parse a menu record."""
        fields = self._record_fields(record)
        return {
            "id": record_id,
            "name": fields.get("name", record_id),
            "parent": fields.get("parent", ""),
            "action": fields.get("action", ""),
            "sequence": fields.get("sequence", "10"),
            "groups": fields.get("groups", ""),
            "file": rel_path,
        }

    def _record_fields(self, record):
        """Extract field values from an Odoo record XML element."""
        fields = {}
        for field_elem in record.findall("field"):
            name = field_elem.get("name", "")
            ref = field_elem.get("re", "")
            eval_val = field_elem.get("eval", "")
            # Get text content or ref/eval
            if ref:
                value = {"re": ref}
            elif eval_val:
                value = {"eval": eval_val}
            else:
                value = field_elem.text or ""
                if field_elem.get("type") == "xml":
                    value = ET.tostring(field_elem, encoding="unicode")
            fields[name] = value
        return fields

    def _detect_view_type(self, arch, fields):
        """Detect view type from arch content or explicit type field."""
        type_field = fields.get("type", "").strip()
        if type_field:
            return type_field
        if not arch:
            return "unknown"
        arch_str = arch if isinstance(arch, str) else str(arch)
        if "<form" in arch_str:
            return "form"
        if "<tree" in arch_str or "<list" in arch_str:
            return "tree"
        if "<kanban" in arch_str:
            return "kanban"
        if "<search" in arch_str:
            return "search"
        if "<graph" in arch_str:
            return "graph"
        if "<pivot" in arch_str:
            return "pivot"
        if "<calendar" in arch_str:
            return "calendar"
        if "<gantt" in arch_str:
            return "gantt"
        if "<activity" in arch_str:
            return "activity"
        if "<qweb" in arch_str:
            return "qweb"
        if "<dashboard" in arch_str:
            return "dashboard"
        if "<cohort" in arch_str:
            return "cohort"
        return "unknown"
