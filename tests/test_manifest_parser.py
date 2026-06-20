import os


class TestFindManifests:
    def test_finds_manifest(self, demo_addon_path):
        from analyzer.parsers.manifest_parser import ManifestParser
        manifests = ManifestParser.find_manifests(demo_addon_path)
        assert "demo_addon" in manifests

    def test_manifest_has_valid_path(self, demo_addon_path):
        from analyzer.parsers.manifest_parser import ManifestParser
        manifests = ManifestParser.find_manifests(demo_addon_path)
        path = manifests["demo_addon"]
        assert os.path.isfile(path)
        assert path.endswith("__manifest__.py")


class TestParseManifest:
    def test_manifest_keys(self, manifest_data):
        assert manifest_data["name"] == "Demo Addon"
        assert manifest_data["version"] == "16.0.1.0.0"
        assert manifest_data["category"] == "Sales"

    def test_manifest_dependencies(self, manifest_data):
        deps = manifest_data["depends"]
        assert "base" in deps
        assert "sale" in deps

    def test_manifest_data_files(self, manifest_data):
        data = manifest_data["data"]
        assert "security/ir.model.access.csv" in data
        assert "views/demo_views.xml" in data

    def test_empty_manifest(self):
        import tempfile
        from analyzer.parsers.manifest_parser import ManifestParser
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("{}")
            path = f.name
        result = ManifestParser.parse_manifest(path)
        os.unlink(path)
        assert result == {}

    def test_invalid_manifest_syntax(self):
        import tempfile
        from analyzer.parsers.manifest_parser import ManifestParser
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("this is not valid python {")
            path = f.name
        result = ManifestParser.parse_manifest(path)
        os.unlink(path)
        assert result == {}
