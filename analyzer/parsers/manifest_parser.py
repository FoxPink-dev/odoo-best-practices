import os
import ast


class ManifestParser:
    """Parse Odoo module manifests (__manifest__.py or __openerp__.py)."""

    @staticmethod
    def find_manifests(addon_dir):
        """Find all manifests in a directory tree (one per addon)."""
        manifests = {}
        for root, dirs, files in os.walk(addon_dir):
            for fname in files:
                if fname in ("__manifest__.py", "__openerp__.py"):
                    addon_name = os.path.basename(root)
                    manifests[addon_name] = os.path.join(root, fname)
        return manifests

    @staticmethod
    def parse_manifest(filepath):
        """Parse a manifest file and return its dict safely."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, UnicodeDecodeError):
            return {}

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            return {}

        manifest = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                for key, val in zip(node.keys, node.values):
                    k = key.s if isinstance(key, ast.Str) else ""
                    v = _ast_to_value(val)
                    if k:
                        manifest[k] = v
                break
        return manifest


def _ast_to_value(node):
    """Convert an AST node to a Python value."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.List):
        return [_ast_to_value(el) for el in node.elts]
    elif isinstance(node, ast.Dict):
        return {k.s: _ast_to_value(v) for k, v in zip(node.keys, node.values) if isinstance(k, ast.Str)}
    elif isinstance(node, ast.NameConstant):
        return node.value
    elif isinstance(node, ast.Tuple):
        return tuple(_ast_to_value(el) for el in node.elts)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        # Handle string concatenation
        left = _ast_to_value(node.left)
        right = _ast_to_value(node.right)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        return None
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "dict":
        return {_ast_to_value(k): _ast_to_value(v) for k, v in zip(node.args[::2], node.args[1::2])}
    return None
