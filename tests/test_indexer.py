class TestIndexer:
    def test_builds_index(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        index = indexer.build()
        assert index["addon"] == "demo_addon"
        assert len(index["models"]) >= 3
        assert len(index["views"]) >= 2
        assert len(index["actions"]) >= 1
        assert len(index["menus"]) >= 1

    def test_search_model(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        indexer.build()
        model = indexer.search_model("demo.order")
        assert model is not None
        assert model["tech_name"] == "demo.order"
        assert model["class_name"] == "DemoOrder"

    def test_search_nonexistent_model(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        indexer.build()
        model = indexer.search_model("nonexistent.model")
        assert model is None

    def test_search_view(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        indexer.build()
        view = indexer.search_view("view_demo_order_form")
        assert view is not None
        assert view["model"] == "demo.order"

    def test_search_action(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        indexer.build()
        action = indexer.search_action("action_demo_order")
        assert action is not None
        assert action["res_model"] == "demo.order"

    def test_fields_for_model(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        indexer.build()
        fields = indexer.fields_for_model("demo.order")
        field_names = [f["name"] for f in fields]
        assert "name" in field_names
        assert "partner_id" in field_names

    def test_methods_for_model(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        indexer.build()
        methods = indexer.methods_for_model("demo.order")
        method_names = [m["name"] for m in methods]
        assert "action_confirm" in method_names

    def test_summary(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        indexer.build()
        summary = indexer.summary()
        assert "Repository:" in summary
        assert "demo_addon" in summary

    def test_to_json(self, demo_addon_path):
        from analyzer.indexer import RepositoryIndex
        indexer = RepositoryIndex(demo_addon_path)
        indexer.build()
        js = indexer.to_json()
        import json
        parsed = json.loads(js)
        assert parsed["addon"] == "demo_addon"
