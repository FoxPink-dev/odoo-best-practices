# -*- coding: utf-8 -*-
"""
Odoo Repository Intelligence - Parser, Graph, Reporter

Analyzes Odoo addon directories to extract:
- Model definitions and inheritance chains
- Field definitions and their characteristics
- View architectures and inheritance
- Security rules (ACL, record rules, groups)
- Module dependencies and manifests
- Controller classes and routes

Outputs structured JSON for AI-powered code review.
"""
from .graph import build_graph, graph_to_mermaid
from .reporter import Reporter
from .store import RepositoryStore

__all__ = ["build_graph", "graph_to_mermaid", "Reporter", "RepositoryStore"]
