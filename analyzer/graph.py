# -*- coding: utf-8 -*-
"""Build dependency graphs from parsed Odoo addon data."""


class InheritanceGraph:
    """Model inheritance graph for a parsed addon."""

    def __init__(self, model_data):
        """
        model_data: dict from ModelParser.get_model_summary()
        """
        self.models = model_data
        self.graph = {}  # tech_name -> set of parent tech_names

    def build(self):
        """Build the inheritance graph."""
        for tech_name, info in self.models.items():
            parents = set()
            # _inherit chain
            inherit_list = info.get("inherit", [])
            if isinstance(inherit_list, list):
                parents.update(inherit_list)
            elif isinstance(inherit_list, str):
                parents.add(inherit_list)

            # _inherits (delegation)
            inherits = info.get("inherits", {})
            if isinstance(inherits, dict):
                parents.update(inherits.keys())

            self.graph[tech_name] = parents
        return self.graph

    def inheritance_chain(self, tech_name):
        """Get full inheritance chain for a model (MRO-like)."""
        visited = set()
        chain = []

        def dfs(name):
            if name in visited:
                return
            visited.add(name)
            chain.append(name)
            for parent in self.graph.get(name, []):
                dfs(parent)

        dfs(tech_name)
        return chain

    def descendants(self, tech_name):
        """Get all models that directly or indirectly inherit from a model."""
        result = set()

        def dfs(name):
            for model, parents in self.graph.items():
                if name in parents and model not in result:
                    result.add(model)
                    dfs(model)

        dfs(tech_name)
        return result

    def roots(self):
        """Get models with no parents (root models)."""
        all_parents = set()
        for parents in self.graph.values():
            all_parents.update(parents)
        return [m for m in self.graph if m not in all_parents]

    def to_dict(self):
        """Return graph as serializable dict."""
        return {m: list(p) for m, p in self.graph.items()}


class ModuleDependencyGraph:
    """Module dependency graph."""

    def __init__(self):
        self.modules = {}  # name -> ManifestParser result
        self.dep_graph = {}  # name -> [dependencies]

    def add_module(self, name, manifest):
        """Add a module with its manifest data."""
        self.modules[name] = manifest
        depends = manifest.get("depends", [])
        if isinstance(depends, list):
            self.dep_graph[name] = depends
        else:
            self.dep_graph[name] = []

    def build(self):
        """Build the dependency graph from all added modules."""
        return self.dep_graph

    def dependency_chain(self, module_name):
        """Get full dependency chain for a module."""
        visited = set()
        chain = []

        def dfs(name):
            if name in visited:
                return
            visited.add(name)
            chain.append(name)
            for dep in self.dep_graph.get(name, []):
                dfs(dep)

        dfs(module_name)
        return chain

    def dependents(self, module_name):
        """Get all modules that depend on a given module."""
        result = []
        for name, deps in self.dep_graph.items():
            if module_name in deps:
                result.append(name)
        return result

    def to_dict(self):
        """Return graph as serializable dict."""
        return dict(self.dep_graph)


def build_graph(model_data, module_deps=None):
    """Build both inheritance and dependency graphs.

    Args:
        model_data: dict from ModelParser.get_model_summary()
        module_deps: dict of {module_name: [dependencies]}

    Returns:
        dict with 'inheritance' and 'dependency' graphs
    """
    ig = InheritanceGraph(model_data)
    ig.build()

    result = {
        "inheritance": ig.to_dict(),
        "roots": ig.roots(),
        "model_count": len(model_data),
    }

    if module_deps:
        mdg = ModuleDependencyGraph()
        for name, deps in module_deps.items():
            mdg.add_module(name, {"depends": deps})
        result["dependency"] = mdg.build()

    return result


def graph_to_mermaid(graph_result, graph_type="inheritance"):
    """Convert a graph result to Mermaid.js diagram format.

    Useful for visualization in AGENTS.md or AI context.
    """
    lines = []

    if graph_type == "inheritance" or "inheritance" in graph_result:
        lines.append("```mermaid")
        lines.append("graph TD")
        graph = graph_result.get("inheritance", {})
        # Group subgraphs by root
        roots = graph_result.get("roots", [])
        if roots:
            for root in roots:
                lines.append("    subgraph " + root + "_family")
                for model, parents in graph.items():
                    if model in graph_result.get("roots", []):
                        continue
                    for p in parents:
                        p_clean = p.replace(".", "_").replace("-", "_")
                        m_clean = model.replace(".", "_").replace("-", "_")
                        lines.append("    " + p_clean + "[" + p + "] --> " + m_clean + "[" + model + "]")
                lines.append("    end")
        # Root models
        for root in roots:
            r_clean = root.replace(".", "_").replace("-", "_")
            lines.append("    " + r_clean + "[" + root + "]")
        lines.append("```")

    if graph_type == "dependency" and "dependency" in graph_result:
        lines.append("```mermaid")
        lines.append("graph LR")
        for module, deps in graph_result.get("dependency", {}).items():
            for dep in deps:
                m_clean = module.replace(".", "_").replace("-", "_")
                d_clean = dep.replace(".", "_").replace("-", "_")
                lines.append("    " + d_clean + "[" + dep + "] --> " + m_clean + "[" + module + "]")
        lines.append("```")

    return "\n".join(lines)
