"""Exercise the evidence boundary in an isolated copy of the public collection."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager


class OfficialEvidenceValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.collection = Path(cls.temp.name) / "collection"
        shutil.copytree(
            Path(__file__).parent / "sealeap-amazon-skills",
            cls.collection,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        cls.name = "sealeap-shopify-agentic-storefront-audit"

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @contextmanager
    def edit(self, relative, transform, as_json=True):
        path = self.collection / relative
        original = path.read_text()
        try:
            value = json.loads(original) if as_json else original
            changed = transform(value)
            path.write_text(json.dumps(changed, ensure_ascii=False) if as_json else changed)
            yield
        finally:
            path.write_text(original)

    def catalog_change(self, change):
        def transform(catalog):
            row = next(x for x in catalog["skills"] if x["name"] == self.name)
            change(row)
            return catalog
        return self.edit("assets/catalog.json", transform)

    def validate(self, expected):
        result = subprocess.run(
            [sys.executable, str(self.collection / "validate_collection.py")],
            capture_output=True, text=True,
        )
        output = json.loads(result.stdout)
        self.assertEqual(output["ok"], expected, output.get("errors"))
        self.assertEqual(result.returncode == 0, expected)

    def test_official_only_package_is_valid_without_fake_engagement(self):
        self.validate(True)

    def test_empty_evidence_cannot_implicitly_claim_official_basis(self):
        with self.catalog_change(lambda row: row.pop("evidence_basis")):
            self.validate(False)

    def test_unregistered_rule_is_not_an_official_source(self):
        with self.catalog_change(lambda row: row.update(rule_checks=["R999"])):
            self.validate(False)

    def test_official_only_package_cannot_have_no_rules(self):
        with self.catalog_change(lambda row: row.update(rule_checks=[])):
            self.validate(False)

    def test_portable_package_must_include_its_official_links(self):
        relative = "shopify/" + self.name + "/references/evidence.md"
        with self.edit(relative, lambda text: text.replace("https://", "removed:"), as_json=False):
            self.validate(False)

    def test_index_excerpt_cannot_back_a_body_verified_package(self):
        def transform(data):
            next(x for x in data["rules"] if x["id"] == "R117")["read_scope"] = "official_index"
            return data
        with self.edit("assets/rule-refresh-20261016.json", transform):
            self.validate(False)

    def test_reverse_rule_mapping_must_agree(self):
        def transform(data):
            next(x for x in data["rules"] if x["id"] == "R117")["used_by"].remove(self.name)
            return data
        with self.edit("assets/rule-refresh-20261016.json", transform):
            self.validate(False)

    def test_adding_rules_does_not_hide_invalid_community_evidence(self):
        with self.catalog_change(lambda row: row.update(sources=["UNKNOWN_SOURCE"])):
            self.validate(False)


if __name__ == "__main__":
    unittest.main()
