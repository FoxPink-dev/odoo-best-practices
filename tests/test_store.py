class TestStore:
    def test_load(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        assert store._loaded is True

    def test_not_loaded_error(self):
        from analyzer.store import RepositoryStore
        store = RepositoryStore("/tmp/fake")
        import pytest
        with pytest.raises(RuntimeError, match="not loaded"):
            store.search_model("test")

    def test_check_code(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        result = store.check_code()
        assert "violations" in result
        assert "summary" in result
        assert result["summary"]["total"] >= 0

    def test_summary(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        s = store.summary()
        assert "demo_addon" in s

    def test_summary_not_loaded(self):
        from analyzer.store import RepositoryStore
        store = RepositoryStore("/tmp/fake")
        s = store.summary()
        assert "not loaded" in s

    def test_list_models(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        models = store.list_models()
        assert len(models) >= 3

    def test_search_model(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        model = store.search_model("demo.order")
        assert model is not None
        assert model["class_name"] == "DemoOrder"

    def test_fields_for_model(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        fields = store.fields_for_model("demo.order")
        assert len(fields) >= 5

    def test_methods_for_model(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        methods = store.methods_for_model("demo.order")
        assert len(methods) >= 5

    def test_inheritance_graph(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        graph = store.inheritance_graph()
        assert isinstance(graph, dict)

    def test_repository_summary(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        summary = store.repository_summary()
        assert summary["addon"] == "demo_addon"

    def test_list_acls(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        acls = store.list_acls()
        assert len(acls) >= 2

    def test_models_missing_acl(self, demo_addon_path):
        from analyzer.store import RepositoryStore
        store = RepositoryStore(demo_addon_path)
        store.load()
        missing = store.models_missing_acl()
        assert "demo.config" in missing
