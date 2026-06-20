import os
import ast
from .common import ast_node_to_value


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
    """Convert an AST node to a Python value. Deprecated: use common.ast_node_to_value."""
    return ast_node_to_value(node)
