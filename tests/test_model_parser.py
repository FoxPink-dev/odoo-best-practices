class TestModelParsing:
    def test_parses_models(self, model_data):
        assert len(model_data.models) >= 3

    def test_demo_order_model(self, model_data):
        model = model_data.models.get("demo.order")
        assert model is not None
        assert model["class_name"] == "DemoOrder"
        assert model["_description"] == "Demo Order"
        assert model["_name"] == "demo.order"

    def test_demo_order_line_model(self, model_data):
        model = model_data.models.get("demo.order.line")
        assert model is not None
        assert model["_description"] == "Demo Order Line"

    def test_transient_model(self, model_data):
        model = model_data.models.get("demo.config")
        assert model is not None
        assert model["class_name"] == "DemoConfig"

    def test_fields_parsed(self, model_data):
        fields = model_data.fields.get("demo.order", [])
        field_names = [f["name"] for f in fields]
        assert "name" in field_names
        assert "partner_id" in field_names
        assert "amount_total" in field_names
        assert "state" in field_names
        assert "line_ids" in field_names

    def test_field_types(self, model_data):
        fields = model_data.fields.get("demo.order", [])
        types = {f["name"]: f["type"] for f in fields}
        assert types.get("name") == "Char"
        assert types.get("partner_id") == "Many2one"
        assert types.get("line_ids") == "One2many"

    def test_methods_parsed(self, model_data):
        methods = model_data.methods.get("demo.order", [])
        method_names = [m["name"] for m in methods]
        assert "action_confirm" in method_names
        assert "action_sql_report" in method_names
        assert "action_sudo_method" in method_names

    def test_method_decorators(self, model_data):
        methods = model_data.methods.get("demo.order", [])
        compute_methods = [m for m in methods if m.get("decorators")]
        assert len(compute_methods) >= 1

    def test_method_code_extracted(self, model_data):
        methods = model_data.methods.get("demo.order", [])
        for m in methods:
            if m["name"] == "action_confirm":
                assert "search" in m.get("code", "")
                break

    def test_no_code_on_syntax_errors(self, model_data):
        for model_methods in model_data.methods.values():
            for m in model_methods:
                assert "code" in m
