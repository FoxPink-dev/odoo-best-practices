import os
import sys
import json

_SKILL_NAME = "odoo-best-practices"
_VERSION = "2.0.0"
_AUTHOR = "FoxPink"


def _rules_count():
    rules_dir = os.path.join(_project_root(), "rules")
    if os.path.isdir(rules_dir):
        return len([f for f in os.listdir(rules_dir) if f.endswith(".md")])
    return 0

_IDE_CONFIGS = {
    "opencode": "OpenCode",
    "claude": "Claude Code",
    "cursor": "Cursor",
    "kiro": "Kiro",
    "windsurf": "Windsurf",
}


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_file(rel_path):
    path = os.path.join(_project_root(), rel_path)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def _read_rules_content():
    return _read_file("AGENTS.md")


def generate_opencode(output_dir):
    rules_count = _rules_count()
    skill = {
        "name": _SKILL_NAME,
        "description": "Odoo development best practices skill pack — %s rules across 13 categories: ORM, security, views, OWL, testing, migration, API, data, i18n, deploy, and anti-pattern detection. Covers Odoo 14-19." % rules_count,
        "version": _VERSION,
        "author": _AUTHOR,
        "license": "MIT",
        "entry": "SKILL.md",
        "triggers": ["odoo", "odoo module", "odoo model", "odoo view",
                     "odoo orm", "odoo security", "odoo owl", "odoo testing",
                     "odoo migration", "odoo api", "odoo data", "odoo i18n",
                     "odoo deploy"],
        "categories": ["module", "orm", "security", "view", "api", "data",
                       "performance", "testing", "migration", "owl", "lint",
                       "code", "i18n", "deploy"],
        "versions": ["14", "15", "16", "17", "18", "19"],
        "mcp": {
            "servers": [
                {
                    "name": "odoo-analyzer",
                    "command": sys.executable,
                    "args": ["-m", "analyzer.mcp_server", "${workspaceRoot}"],
                    "description": "Odoo static analysis: model/field/view/security queries, code checking, repository intelligence",
                }
            ]
        },
        "tools": [
            {"name": "analyze_module",
             "description": "Full Odoo addon analysis: models, views, security, dependencies, violations"},
            {"name": "search_model",
             "description": "Find Odoo model definition with fields, methods, inheritance chain"},
            {"name": "check_repository",
             "description": "Run AST rule engine + security audit on an Odoo addon"},
            {"name": "explain_model",
             "description": "Rich Odoo model explanation combining parsed data + domain knowledge"},
        ],
        "analysis": {
            "static": {
                "parsers": ["manifest", "model", "view", "security"],
                "engine": "AST (no eval, no runtime)",
                "rules": _rules_count(),
                "anti_patterns": 12,
                "supported_versions": ["14", "15", "16", "17", "18", "19"],
            }
        },
    }
    target_dir = os.path.join(output_dir, ".opencode")
    os.makedirs(target_dir, exist_ok=True)
    skill_path = os.path.join(target_dir, "skill.json")
    with open(skill_path, "w", encoding="utf-8") as f:
        json.dump(skill, f, indent=2)
    return skill_path


def generate_claude(output_dir, content):
    target_dir = os.path.join(output_dir, ".claude", "rules")
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, "odoo-best-practices.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def generate_cursor(output_dir, content):
    target_dir = os.path.join(output_dir, ".cursor", "rules")
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, "odoo-best-practices.mdc")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("description: Odoo development best practices (%s rules)\n" % _rules_count())
        f.write("globs: \"**/*.py\"\n")
        f.write("---\n")
        f.write(content)
    return filepath


def generate_kiro(output_dir, content):
    target_dir = os.path.join(output_dir, ".kiro", "steering")
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, "odoo-best-practices.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("include: always\n")
        f.write("fileMatchPattern: \"**/*.py\"\n")
        f.write("---\n")
        f.write(content)
    return filepath


def generate_windsurf(output_dir, content):
    target_dir = os.path.join(output_dir, ".windsurf", "rules")
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, "odoo-best-practices.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("trigger: always_on\n")
        f.write("---\n")
        f.write(content)
    return filepath


_GENERATORS = {
    "opencode": generate_opencode,
    "claude": generate_claude,
    "cursor": generate_cursor,
    "kiro": generate_kiro,
    "windsurf": generate_windsurf,
}


def generate(ide, output_dir="."):
    """Generate IDE configuration for odoo-best-practices.

    Args:
        ide: One of "opencode", "claude", "cursor", "kiro", "windsurf", or "all".
        output_dir: Target project directory (default: current directory).

    Returns:
        List of (ide_name, file_path) tuples for generated files.
    """
    output_dir = os.path.abspath(output_dir)
    content = _read_rules_content() if ide != "opencode" else ""
    generated = []

    if ide == "all":
        for name, gen in _GENERATORS.items():
            if name == "opencode":
                fp = gen(output_dir)
            else:
                fp = gen(output_dir, content)
            generated.append((name, fp))
    else:
        if ide not in _GENERATORS:
            raise ValueError("Unknown IDE '%s'. Choose: %s" % (
                ide, ", ".join(sorted(_GENERATORS.keys()))))
        gen = _GENERATORS[ide]
        fp = gen(output_dir, content) if ide != "opencode" else gen(output_dir)
        generated.append((ide, fp))

    return generated
