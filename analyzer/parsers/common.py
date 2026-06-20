import ast
import sys


def ast_node_to_value(node):
    """Convert an AST node to a Python value.

    Handles Python 3.8+ (ast.Constant) and legacy (ast.Str, ast.Num) nodes
    for compatibility with Odoo codebases running on Python 3.6+.
    """
    Constant = getattr(ast, 'Constant', None)
    if Constant is not None and isinstance(node, Constant):
        return node.value
    if sys.version_info < (3, 8):
        if isinstance(node, ast.Str):
            return node.s
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.NameConstant):
            return node.value
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.List):
        return [ast_node_to_value(el) for el in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(ast_node_to_value(el) for el in node.elts)
    elif isinstance(node, ast.Set):
        return {ast_node_to_value(el) for el in node.elts}
    elif isinstance(node, ast.Dict):
        result = {}
        for k, v in zip(node.keys, node.values):
            key = ast_node_to_value(k)
            if key is not None:
                result[key] = ast_node_to_value(v)
        return result
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        val = ast_node_to_value(node.operand)
        return -val if isinstance(val, (int, float)) else None
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = ast_node_to_value(node.left)
        right = ast_node_to_value(node.right)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        return None
    elif isinstance(node, ast.Call):
        return None
    return None
