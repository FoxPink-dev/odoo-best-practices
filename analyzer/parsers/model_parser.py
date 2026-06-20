# -*- coding: utf-8 -*-
import os
import ast


class ModelParser:
    """Parse Odoo Python files to extract model definitions, fields, inheritance."""

    MODEL_CLASSES = {"models.Model", "models.TransientModel", "models.AbstractModel"}

    def __init__(self):
        self.models = {}        # model_tech_name -> ModelInfo
        self.fields = {}         # model_tech_name -> [FieldInfo]
        self.methods = {}        # model_tech_name -> [MethodInfo]

    def parse_addon(self, addon_dir):
        """Recursively parse all Python files in an addon directory."""
        for root, dirs, files in os.walk(addon_dir):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "migrations", "static")]
            for fname in files:
                if fname.endswith(".py") and fname != "__manifest__.py":
                    filepath = os.path.join(root, fname)
                    self._parse_py_file(filepath, addon_dir)

    def _parse_py_file(self, filepath, addon_dir):
        """Parse a single Python file for Odoo model definitions."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
        except (IOError, UnicodeDecodeError):
            return

        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            return

        rel_path = os.path.relpath(filepath, addon_dir).replace("\\", "/")

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._parse_class(node, rel_path)

    def _parse_class(self, node, rel_path):
        """Parse a single class definition for Odoo model info."""
        bases = [self._base_name(b) for b in node.bases]
        is_odoo_model = any(b in self.MODEL_CLASSES for b in bases)
        if not is_odoo_model:
            return

        model_info = {
            "class_name": node.name,
            "file": rel_path,
            "line": node.lineno,
            "bases": bases,
            "_name": None,
            "_inherit": None,
            "_inherits": None,
            "_description": None,
            "_rec_name": None,
            "_order": None,
            "_sql_constraints": None,
            "has_auto_init": False,
        }

        # Extract class-level dunder attributes (_name, _inherit, _description, etc.)
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id.startswith('_'):
                        model_info[target.id] = self._get_assigned_value(item)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name) and item.target.id.startswith('_'):
                    if item.value:
                        model_info[item.target.id] = self._get_assigned_value(item)

        tech_name = model_info.get("_name") or model_info.get("_inherit")
        if not tech_name:
            return

        if isinstance(tech_name, list):
            tech_name = tech_name[0] if tech_name else None
        if not tech_name:
            return

        model_info["_inherit"] = self._normalize_inherit(model_info.get("_inherit"))
        model_info["_inherits"] = model_info.get("_inherits") or {}

        self.models[tech_name] = model_info

        # Extract fields and methods
        self.fields[tech_name] = self._extract_fields(node, rel_path)
        self.methods[tech_name] = self._extract_methods(node, rel_path)

    def _extract_fields(self, class_node, rel_path):
        """Extract field definitions from a model class."""
        fields = []
        for item in class_node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        field_info = self._parse_field_assignment(target.id, item, rel_path)
                        if field_info:
                            fields.append(field_info)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name) and not item.target.id.startswith("_"):
                    field_info = self._parse_field_annotation(item.target.id, item, rel_path)
                    if field_info:
                        fields.append(field_info)
        return fields

    def _parse_field_assignment(self, field_name, node, rel_path):
        """Parse a field assignment like name = fields.Char(...)."""
        if not isinstance(node.value, ast.Call):
            return None
        call = node.value
        if not isinstance(call.func, ast.Attribute):
            return None
        field_type = "{self._safe_name(call.func.value)}.{call.func.attr}" if isinstance(call.func.value, ast.Name) else call.func.attr

        if "fields." not in field_type and "odoo.fields." not in field_type:
            return None

        params = self._extract_call_keywords(call)

        return {
            "name": field_name,
            "type": params.pop("_type_hint", field_type.split(".")[-1]),
            "line": node.lineno,
            "params": params,
        }

    def _parse_field_annotation(self, field_name, node, rel_path):
        """Parse an annotated field assignment."""
        if node.value is None:
            return None
        if not isinstance(node.value, ast.Call):
            return None
        call = node.value
        if not isinstance(call.func, ast.Attribute):
            return None
        field_type = call.func.attr
        params = self._extract_call_keywords(call)
        return {
            "name": field_name,
            "type": field_type,
            "line": node.lineno,
            "params": params,
        }

    def _extract_methods(self, class_node, rel_path):
        """Extract method definitions, especially Odoo-decorated ones."""
        methods = []
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    "name": item.name,
                    "line": item.lineno,
                    "decorators": [],
                }
                for dec in item.decorator_list:
                    dec_name = self._decorator_name(dec)
                    if dec_name:
                        method_info["decorators"].append(dec_name)
                methods.append(method_info)
        return methods

    def _extract_call_keywords(self, call_node):
        """Extract keyword arguments from a function call."""
        params = {}
        for kw in call_node.keywords:
            if kw.arg is None:
                continue
            params[kw.arg] = self._ast_val_to_str(kw.value)
        return params

    def _base_name(self, node):
        """Convert a base class AST node to string name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return "{self._base_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return "{self._base_name(node.value)}[{self._base_name(node.slice)}]"
        return str(node)

    def _safe_name(self, node):
        """Safely extract a name from a Name node."""
        if isinstance(node, ast.Name):
            return node.id
        return str(node)

    def _decorator_name(self, node):
        """Convert a decorator AST node to string."""
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            return "{self._base_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Attribute):
            return "{node.value.id}.{node.attr}" if isinstance(node.value, ast.Name) else node.attr
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            return self._decorator_name(node.func)
        return None

    def _get_assigned_value(self, node):
        """Get the value from an assignment node."""
        if isinstance(node, ast.Assign):
            return _ast_to_value(node.value)
        elif isinstance(node, ast.AnnAssign) and node.value:
            return _ast_to_value(node.value)
        return None

    def _normalize_inherit(self, inherit):
        """Normalize _inherit to always be a list."""
        if inherit is None:
            return []
        if isinstance(inherit, str):
            return [inherit]
        if isinstance(inherit, list):
            return inherit
        return []

    def _ast_val_to_str(self, node):
        """Convert AST value node to a string representation."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, ast.List):
            return [_ast_to_value(el) for el in node.elts]
        elif isinstance(node, ast.Dict):
            return {}
        elif isinstance(node, ast.Name):
            return "ref:{node.id}"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "fields":
            arg0 = node.args[0] if node.args else None
            val = _ast_to_value(arg0) if arg0 else None
            return "fields.{val}" if val else None
        elif isinstance(node, ast.Attribute):
            return "{self._ast_val_to_str(node.value)}.{node.attr}" if node.value else node.attr
        return None

    def get_model_summary(self):
        """Get a summary of all parsed models."""
        return {
            tech_name: {
                "class": info["class_name"],
                "file": info["file"],
                "inherit": self._normalize_inherit(info["_inherit"]),
                "inherits": info["_inherits"],
                "description": info["_description"],
                "fields": len(self.fields.get(tech_name, [])),
                "methods": len(self.methods.get(tech_name, [])),
            }
            for tech_name, info in self.models.items()
        }


def _ast_to_value(node):
    """AST node to Python value (handles Python 3.8+ ast.Constant)."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.NameConstant):
        return node.value
    elif isinstance(node, ast.List):
        return [_ast_to_value(el) for el in node.elts]
    elif isinstance(node, ast.Dict):
        return {
            _ast_to_value(k): _ast_to_value(v)
            for k, v in zip(node.keys, node.values)
            if _ast_to_value(k) is not None
        }
    elif isinstance(node, ast.Tuple):
        return tuple(_ast_to_value(el) for el in node.elts)
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        val = _ast_to_value(node.operand)
        return -val if isinstance(val, (int, float)) else None
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _ast_to_value(node.left)
        right = _ast_to_value(node.right)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        return None
    elif isinstance(node, ast.Call):
        return None
    elif isinstance(node, ast.Set):
        return {_ast_to_value(el) for el in node.elts}
    return None
