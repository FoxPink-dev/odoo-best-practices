# -*- coding: utf-8 -*-
import os
import csv
import io
import xml.etree.ElementTree as ET


class SecurityParser:
    """Parse Odoo security artifacts: ACLs, Record Rules, Groups, Categories."""

    def __init__(self):
        self.acls = []                 # [ACLInfo]
        self.record_rules = []         # [RuleInfo]
        self.groups = []               # [GroupInfo]
        self.categories = []           # [CategoryInfo]

    def parse_addon(self, addon_dir):
        """Parse all security-related files in an addon directory."""
        security_dir = os.path.join(addon_dir, "security")
        if os.path.isdir(security_dir):
            for fname in os.listdir(security_dir):
                filepath = os.path.join(security_dir, fname)
                rel_path = f"security/{fname}"
                if fname.endswith(".csv"):
                    self._parse_acl_csv(filepath)
                elif fname.endswith(".xml"):
                    self._parse_security_xml(filepath, rel_path)

        # Also scan other directories for CSV files
        for root, dirs, files in os.walk(addon_dir):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "migrations", "static")]
            for fname in files:
                if fname.endswith(".csv") and "security" not in root:
                    filepath = os.path.join(root, fname)
                    if "ir.model.access" in fname.lower() or "acl" in fname.lower():
                        self._parse_acl_csv(filepath)

        # Check CSV data files in any subdirectory for acl patterns
        for root, dirs, files in os.walk(addon_dir):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "migrations", "static")]
            for fname in files:
                if fname.endswith(".csv"):
                    filepath = os.path.join(root, fname)
                    with open(filepath, "r", encoding="utf-8") as f:
                        header = f.readline()
                        if "id,name,model_id,group_id,perm_read" in header.lower():
                            self._parse_acl_csv(filepath)

    def _parse_acl_csv(self, filepath):
        """Parse an ACL CSV file (ir.model.access.csv)."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, UnicodeDecodeError):
            return

        reader = csv.DictReader(io.StringIO(content))
        for row in reader:
            # Normalise Odoo CSV column names (strip :id, :eval suffixes)
            normalised = {}
            for k, v in row.items():
                clean = k.split(":")[0] if k else k
                normalised[clean] = v
            self.acls.append({
                "id": normalised.get("id", ""),
                "name": normalised.get("name", ""),
                "model_id": normalised.get("model_id", ""),
                "group_id": normalised.get("group_id", ""),
                "perm_read": normalised.get("perm_read", "0"),
                "perm_write": normalised.get("perm_write", "0"),
                "perm_create": normalised.get("perm_create", "0"),
                "perm_unlink": normalised.get("perm_unlink", "0"),
            })

    def _parse_security_xml(self, filepath, rel_path):
        """Parse security XML (groups, categories, record rules)."""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except (ET.ParseError, IOError):
            return

        for record in root.iter("record"):
            model = record.get("model", "")
            record_id = record.get("id", "")

            if model == "ir.module.category":
                fields = self._record_fields(record)
                self.categories.append({
                    "id": record_id,
                    "name": fields.get("name", record_id),
                    "parent": fields.get("parent_id", ""),
                    "description": fields.get("description", ""),
                    "file": rel_path,
                })

            elif model == "res.groups":
                fields = self._record_fields(record)
                self.groups.append({
                    "id": record_id,
                    "name": fields.get("name", record_id),
                    "category_id": fields.get("category_id", ""),
                    "implied_ids": fields.get("implied_ids", ""),
                    "users": fields.get("users", ""),
                    "comment": fields.get("comment", ""),
                    "file": rel_path,
                })

            elif model == "ir.rule":
                fields = self._record_fields(record)
                self.record_rules.append({
                    "id": record_id,
                    "name": fields.get("name", record_id),
                    "model_id": fields.get("model_id", ""),
                    "domain_force": fields.get("domain_force", ""),
                    "groups": fields.get("groups", ""),
                    "perm_read": fields.get("perm_read", "True"),
                    "perm_write": fields.get("perm_write", "True"),
                    "perm_create": fields.get("perm_create", "True"),
                    "perm_unlink": fields.get("perm_unlink", "True"),
                    "global": fields.get("global", ""),
                    "file": rel_path,
                })

            elif model in ("ir.model.access",):
                fields = self._record_fields(record)
                self.acls.append({
                    "id": record_id,
                    "name": fields.get("name", record_id),
                    "model_id": fields.get("model_id", ""),
                    "group_id": fields.get("group_id", ""),
                    "perm_read": fields.get("perm_read", "0"),
                    "perm_write": fields.get("perm_write", "0"),
                    "perm_create": fields.get("perm_create", "0"),
                    "perm_unlink": fields.get("perm_unlink", "0"),
                })

    def _record_fields(self, record):
        """Extract field values from an Odoo record XML element."""
        fields = {}
        for field_elem in record.findall("field"):
            name = field_elem.get("name", "")
            ref = field_elem.get("re", "")
            eval_val = field_elem.get("eval", "")
            if ref:
                value = {"re": ref}
            elif eval_val:
                value = {"eval": eval_val}
            else:
                value = field_elem.text or ""
            fields[name] = value
        return fields
