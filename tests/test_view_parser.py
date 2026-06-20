class TestViewParsing:
    def test_parses_views(self, view_data):
        assert len(view_data.views) >= 2

    def test_form_view(self, view_data):
        form_views = [v for v in view_data.views if v["type"] == "form"]
        assert len(form_views) >= 1
        form = form_views[0]
        assert form["model"] == "demo.order"
        assert form["id"] == "view_demo_order_form"

    def test_tree_view(self, view_data):
        tree_views = [v for v in view_data.views if v["type"] == "tree"]
        assert len(tree_views) >= 1
        tree = tree_views[0]
        assert tree["id"] == "view_demo_order_tree"

    def test_action_parsed(self, view_data):
        actions = [a for a in view_data.actions if a["id"] == "action_demo_order"]
        assert len(actions) == 1
        action = actions[0]
        assert action["res_model"] == "demo.order"
        assert action["view_mode"] == "tree,form"

    def test_menu_parsed(self, view_data):
        menus = [m for m in view_data.menus if m["id"] == "menu_demo_order"]
        assert len(menus) == 1
        menu = menus[0]
        assert menu["name"] == "Demo Orders"
        assert menu["action"] == "action_demo_order"

    def test_view_fields(self, view_data):
        for v in view_data.views:
            assert "id" in v
            assert "name" in v
            assert "model" in v
            assert "type" in v
            assert "file" in v

    def test_view_file_path(self, view_data):
        for v in view_data.views:
            assert "demo_views.xml" in v["file"]
