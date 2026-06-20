class TestSecurityParsing:
    def test_parses_acls(self, security_data):
        assert len(security_data.acls) >= 2

    def test_acl_entry_format(self, security_data):
        acl = security_data.acls[0]
        assert "id" in acl
        assert "model_id" in acl
        assert "group_id" in acl
        assert "perm_read" in acl
        assert "perm_write" in acl
        assert "perm_create" in acl
        assert "perm_unlink" in acl

    def test_acl_model_id_format(self, security_data):
        for acl in security_data.acls:
            assert acl["model_id"].startswith("model_"), "model_id should be XML-ID format"

    def test_demo_order_acl_found(self, security_data):
        model_ids = [a["model_id"] for a in security_data.acls]
        assert "model_demo_order" in model_ids
        assert "model_demo_order_line" in model_ids

    def test_acl_permissions(self, security_data):
        for acl in security_data.acls:
            if acl["id"] == "access_demo_order_user":
                assert acl["perm_read"] == "1"
                assert acl["perm_write"] == "1"
                assert acl["perm_create"] == "1"
                assert acl["perm_unlink"] == "0"

    def test_no_groups_if_none_declared(self, security_data):
        assert security_data.groups == []

    def test_no_categories_if_none_declared(self, security_data):
        assert security_data.categories == []

    def test_no_record_rules_if_none_declared(self, security_data):
        assert security_data.record_rules == []
