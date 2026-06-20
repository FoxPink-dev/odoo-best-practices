class TestInheritanceGraph:
    def test_build_graph(self, model_data):
        from analyzer.graph import InheritanceGraph
        summary = model_data.get_model_summary()
        graph = InheritanceGraph(summary)
        result = graph.build()
        assert len(result) >= 3
        assert "demo.order" in result

    def test_roots(self, model_data):
        from analyzer.graph import InheritanceGraph
        graph = InheritanceGraph(model_data.get_model_summary())
        graph.build()
        roots = graph.roots()
        assert "demo.order" in roots


class TestMermaidOutput:
    def test_graph_to_mermaid_inheritance(self, model_data):
        from analyzer.graph import build_graph, graph_to_mermaid
        result = build_graph(model_data.get_model_summary())
        mermaid = graph_to_mermaid(result, "inheritance")
        assert "```mermaid" in mermaid
        assert "graph TD" in mermaid

    def test_graph_to_mermaid_unknown_type(self, model_data):
        from analyzer.graph import build_graph, graph_to_mermaid
        result = build_graph(model_data.get_model_summary())
        mermaid = graph_to_mermaid(result, "unknown")
        assert mermaid == ""


class TestModuleDependencyGraph:
    def test_add_module(self, manifest_data):
        from analyzer.graph import ModuleDependencyGraph
        mdg = ModuleDependencyGraph()
        mdg.add_module("demo_addon", manifest_data)
        graph = mdg.build()
        assert "demo_addon" in graph
        assert "base" in graph["demo_addon"]

    def test_dependency_chain(self, manifest_data):
        from analyzer.graph import ModuleDependencyGraph
        mdg = ModuleDependencyGraph()
        mdg.add_module("demo_addon", manifest_data)
        chain = mdg.dependency_chain("demo_addon")
        assert "demo_addon" in chain
        assert "base" in chain
