import os
import pytest

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "demo_addon")


@pytest.fixture
def demo_addon_path():
    return FIXTURE_DIR


@pytest.fixture
def manifest_data(demo_addon_path):
    from analyzer.parsers.manifest_parser import ManifestParser
    manifests = ManifestParser.find_manifests(demo_addon_path)
    name = os.path.basename(demo_addon_path)
    return ManifestParser.parse_manifest(manifests[name])


@pytest.fixture
def model_data(demo_addon_path):
    from analyzer.parsers.model_parser import ModelParser
    parser = ModelParser()
    parser.parse_addon(demo_addon_path)
    return parser


@pytest.fixture
def view_data(demo_addon_path):
    from analyzer.parsers.view_parser import ViewParser
    parser = ViewParser()
    parser.parse_addon(demo_addon_path)
    return parser


@pytest.fixture
def security_data(demo_addon_path):
    from analyzer.parsers.security_parser import SecurityParser
    parser = SecurityParser()
    parser.parse_addon(demo_addon_path)
    return parser


@pytest.fixture
def all_results(demo_addon_path):
    from analyzer.reporter import Reporter
    reporter = Reporter(demo_addon_path)
    return reporter.run()


@pytest.fixture
def full_checker_results(all_results):
    from analyzer.checker import Checker
    checker = Checker(all_results)
    violations = checker.run_all()
    return {"violations": violations, "summary": checker.summary()}
