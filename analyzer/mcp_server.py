# -*- coding: utf-8 -*-
"""
Odoo Static Analysis MCP Server

Exposes the RepositoryStore via the Model Context Protocol (MCP)
so AI agents (Cursor, Claude Code, OpenCode) can query repository
intelligence directly.

Protocol: JSON-RPC 2.0 over stdin/stdout
Schema: MCP (Model Context Protocol) rev 2025-03-26

Usage:
    python -m analyzer.mcp_server /path/to/addon

Or via OpenCode/Cursor MCP config:
    {
        "mcpServers": {
            "odoo-analyzer": {
                "command": "python",
                "args": ["-m", "analyzer.mcp_server", "/path/to/addon"]
            }
        }
    }
"""

import json
import sys
import os
import traceback
from .store import RepositoryStore
from .constants import SEVERITY_ORDER


# ------------------------------------------------------------------
# MCP Protocol helpers
# ------------------------------------------------------------------

def jsonrpc_error(id_, code, message, data=None):
    resp = {
        "jsonrpc": "2.0",
        "id": id_,
        "error": {"code": code, "message": message},
    }
    if data is not None:
        resp["error"]["data"] = data
    return resp


def jsonrpc_result(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def jsonrpc_notification(method, params=None):
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    return msg


# ------------------------------------------------------------------
# Tool definitions (MCP tool schema)
# ------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "analyze_module",
        "description": "Analyze a complete Odoo addon module: models, views, security, dependencies, and issues",
        "inputSchema": {
            "type": "object",
            "properties": {
                "addon_dir": {
                    "type": "string",
                    "description": "Path to the Odoo addon directory",
                }
            },
            "required": ["addon_dir"],
        },
    },
    {
        "name": "search_model",
        "description": "Find a model's complete definition: fields, methods, inheritance, views, actions, menus, ACLs, record rules, dependencies, and extending models",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Technical model name (e.g. sale.order)",
                }
            },
            "required": ["model_name"],
        },
    },
    {
        "name": "search_view",
        "description": "Find a view's complete definition: architecture, model, inheritance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "view_id": {
                    "type": "string",
                    "description": "View XML ID (e.g. sale_order_form)",
                }
            },
            "required": ["view_id"],
        },
    },
    {
        "name": "search_action",
        "description": "Find an action definition and its linked views/menus",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action_id": {
                    "type": "string",
                    "description": "Action XML ID (e.g. action_orders)",
                }
            },
            "required": ["action_id"],
        },
    },
    {
        "name": "check_repository",
        "description": "Run full static analysis: AST rule engine + security audit + bad pattern detection",
        "inputSchema": {
            "type": "object",
            "properties": {
                "addon_dir": {
                    "type": "string",
                    "description": "Path to the Odoo addon directory",
                },
                "severity": {
                    "type": "string",
                    "description": "Minimum severity filter (CRITICAL, HIGH, MEDIUM, LOW)",
                    "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                },
            },
            "required": ["addon_dir"],
        },
    },
    {
        "name": "explain_model",
        "description": "Get a rich explanation of a model: fields, methods, views, actions, knowledge base docs, inheritance chain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Technical model name (e.g. sale.order)",
                }
            },
            "required": ["model_name"],
        },
    },
    {
        "name": "list_models",
        "description": "List all models in the repository with their tech names and modules",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "list_views",
        "description": "List all views in the repository",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "list_actions",
        "description": "List all actions in the repository",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "repository_summary",
        "description": "Get a high-level summary of the repository: model count, field count, view count, violations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "addon_dir": {
                    "type": "string",
                    "description": "Path to the Odoo addon directory",
                }
            },
            "required": ["addon_dir"],
        },
    },
    {
        "name": "models_missing_acl",
        "description": "Find models that are declared but have no ACL entries (security audit)",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "inheritance_graph",
        "description": "Get the full model inheritance graph as Mermaid diagram text",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "build_index",
        "description": "Rebuild the repository index for faster subsequent queries",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "list_knowledge_topics",
        "description": "List available domain knowledge topics (model documentation)",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ------------------------------------------------------------------
# MCP Server
# ------------------------------------------------------------------

class MCPServer:
    """MCP server exposing the Odoo analyzer toolset."""

    def __init__(self, addon_dir):
        self.addon_dir = os.path.abspath(addon_dir)
        self.store = RepositoryStore(self.addon_dir)
        self._initialized = False
        self._tools = {t["name"]: t for t in TOOL_DEFINITIONS}

    # ------------------------------------------------------------------
    # Handle incoming requests
    # ------------------------------------------------------------------

    def handle_request(self, request):
        """Process a single JSON-RPC request/notification."""
        req_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            return self._handle_initialize(req_id, params)
        elif method == "tools/list":
            return self._handle_list_tools(req_id)
        elif method == "tools/call":
            return self._handle_call_tool(req_id, params)
        elif method == "notifications/initialized":
            # No response expected
            return None
        else:
            return jsonrpc_error(req_id, -32601, f"Method not found: {method}")

    def _handle_initialize(self, req_id, params):
        self._initialized = True
        return jsonrpc_result(req_id, {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": "odoo-analyzer",
                "version": "2.0.0",
            },
            "instructions": (
                "Odoo Static Analysis MCP Server. "
                "Analyzes Odoo addon repositories using AST parsing, "
                "rule engines, and domain knowledge. "
                "Use tools: analyze_module, search_model, search_view, "
                "check_repository, explain_model."
            ),
        })

    def _handle_list_tools(self, req_id):
        return jsonrpc_result(req_id, {
            "tools": list(self._tools.values()),
        })

    def _handle_call_tool(self, req_id, params):
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name not in self._tools:
            return jsonrpc_error(req_id, -32602, f"Unknown tool: {tool_name}")

        # Get effective addon dir: tool argument overrides server default
        effective_dir = arguments.get("addon_dir", self.addon_dir)

        # Load store if not already loaded for this addon
        if effective_dir != getattr(self, "_loaded_dir", None):
            self._loaded_dir = effective_dir
            self.store = RepositoryStore(effective_dir)
            self.store.load()

        handler = getattr(self, f"tool_{tool_name}", None)
        if handler is None:
            return jsonrpc_error(req_id, -32603, f"Tool {tool_name} not implemented")

        try:
            result = handler(effective_dir, arguments)
            return jsonrpc_result(req_id, result)
        except Exception as e:
            return jsonrpc_error(req_id, -32603, str(e), traceback.format_exc())

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    def tool_analyze_module(self, addon_dir, arguments):
        """Full module analysis: models, views, security, dependencies, issues."""
        summary = self.store.repository_summary()
        models = self.store.list_models()
        views = self.store.list_views()
        actions = self.store.list_actions()
        acls = self.store.list_acls()
        rules = self.store.list_record_rules()
        violations = self.store.check_code()
        deps = self.store.dependency_graph()
        missing_acl = self.store.models_missing_acl()

        return {
            "summary": summary,
            "models": models,
            "views_count": len(views),
            "views": views[:10],  # Limit to avoid context overflow
            "actions_count": len(actions),
            "acls_count": len(acls),
            "record_rules_count": len(rules),
            "dependencies": deps,
            "models_missing_acl": missing_acl,
            "violations_summary": violations.get("summary", {}),
            "violations": violations.get("violations", [])[:20],
        }

    def tool_search_model(self, addon_dir, arguments):
        model_name = arguments.get("model_name", "")
        if not model_name:
            return {"error": "model_name is required"}

        # Build rich model context
        model = self.store.search_model(model_name)
        if not model:
            return {"error": f"Model '{model_name}' not found"}

        fields = self.store.fields_for_model(model_name)
        methods = self.store.methods_for_model(model_name)
        chain = self.store.model_inheritance_chain(model_name)
        extending = self.store.models_extending(model_name)
        related_views = [v for v in self.store.list_views() if v.get("model") == model_name]
        related_actions = [a for a in self.store.list_actions() if a.get("res_model") == model_name]
        related_menus = self.store.menus_for_model(model_name)
        acl_entries = self.store.acls_for_model(model_name)
        rule_entries = self.store.record_rules_for_model(model_name)
        deps = self.store.model_dependencies()

        return {
            "model": model,
            "module": model.get("file", "").split("/")[0] if model.get("file") else "",
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
        }

    def tool_search_view(self, addon_dir, arguments):
        view_id = arguments.get("view_id", "")
        if not view_id:
            return {"error": "view_id is required"}

        view = self.store.search_view(view_id)
        if not view:
            return {"error": f"View '{view_id}' not found"}

        chain = self.store.view_inheritance_chain(view_id)
        return {
            "view": view,
            "inheritance_chain": chain,
        }

    def tool_search_action(self, addon_dir, arguments):
        action_id = arguments.get("action_id", "")
        if not action_id:
            return {"error": "action_id is required"}

        action = self.store.search_action(action_id)
        if not action:
            return {"error": f"Action '{action_id}' not found"}

        return {"action": action}

    def tool_check_repository(self, addon_dir, arguments):
        violations_data = self.store.check_code()
        violations = violations_data.get("violations", [])
        min_severity = arguments.get("severity", "LOW").upper()
        min_level = SEVERITY_ORDER.get(min_severity, 3)

        filtered = [
            v for v in violations
            if SEVERITY_ORDER.get(v.get("severity", "LOW").upper(), 3) <= min_level
        ]

        missing_acl = self.store.models_missing_acl()

        return {
            "summary": violations_data.get("summary", {}),
            "violations": filtered,
            "violations_count": len(filtered),
            "models_missing_acl": missing_acl,
            "models_missing_acl_count": len(missing_acl),
        }

    def tool_explain_model(self, addon_dir, arguments):
        model_name = arguments.get("model_name", "")
        if not model_name:
            return {"error": "model_name is required"}

        explanation = self.store.explain_model(model_name)
        if not explanation.get("model"):
            return {"error": f"Model '{model_name}' not found"}

        # Limit fields
        fields_list = explanation.get("fields", [])
        if len(fields_list) > 30:
            explanation["fields"] = fields_list[:30]
            explanation["fields_truncated"] = len(fields_list) - 30
        else:
            explanation["fields_truncated"] = 0

        return explanation

    def tool_list_models(self, addon_dir, arguments):
        return {"models": self.store.list_models()}

    def tool_list_views(self, addon_dir, arguments):
        return {"views": self.store.list_views()}

    def tool_list_actions(self, addon_dir, arguments):
        return {"actions": self.store.list_actions()}

    def tool_repository_summary(self, addon_dir, arguments):
        summary = self.store.repository_summary()
        graph = self.store.inheritance_graph_mermaid()
        return {
            "summary": summary,
            "inheritance_graph_mermaid": graph,
        }

    def tool_models_missing_acl(self, addon_dir, arguments):
        return {"models_missing_acl": self.store.models_missing_acl()}

    def tool_inheritance_graph(self, addon_dir, arguments):
        return {
            "inheritance_graph": self.store.inheritance_graph(),
            "mermaid": self.store.inheritance_graph_mermaid(),
        }

    def tool_build_index(self, addon_dir, arguments):
        self.store.load(reindex=True)
        return {"status": "ok", "message": "Repository index rebuilt"}

    def tool_list_knowledge_topics(self, addon_dir, arguments):
        return {"topics": self.store.list_knowledge_topics()}


# ------------------------------------------------------------------
# Entry point — stdio transport
# ------------------------------------------------------------------

def main():
    """Run the MCP server over stdin/stdout."""
    if len(sys.argv) < 2:
        print("Usage: python -m analyzer.mcp_server <addon_dir>", file=sys.stderr)
        sys.exit(1)

    addon_dir = sys.argv[1]
    if not os.path.isdir(addon_dir):
        print(f"Error: not a directory: {addon_dir}", file=sys.stderr)
        sys.exit(1)

    server = MCPServer(addon_dir)

    # Send server->client initialized notification
    init_notification = json.dumps(jsonrpc_notification("initialized"))
    sys.stdout.write(init_notification + "\n")
    sys.stdout.flush()

    # Main loop: read JSON-RPC from stdin, write responses to stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            # Can't send error without a valid ID
            sys.stderr.write(f"JSON decode error: {e}\n")
            sys.stderr.flush()
            continue

        try:
            response = server.handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_resp = jsonrpc_error(request.get("id"), -32603, str(e))
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
