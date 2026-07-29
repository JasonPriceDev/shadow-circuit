from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts/sdlc"
sys.path.insert(0, str(SCRIPT_DIR))

import traceability  # noqa: E402


class TraceabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.original_root = traceability.ROOT
        traceability.ROOT = self.root

    def tearDown(self) -> None:
        traceability.ROOT = self.original_root
        self.temp.cleanup()

    def _write_manifest(self, artifacts: list[dict]) -> Path:
        path = self.root / "manifest.json"
        path.write_text(
            json.dumps({"schema_version": 1, "artifacts": artifacts}),
            encoding="utf-8",
        )
        return path

    def test_detects_changed_parent_and_affected_child(self) -> None:
        concept = self.root / "docs/concept.md"
        spec = self.root / "docs/spec.md"
        concept.parent.mkdir(parents=True)
        concept.write_text("concept v1", encoding="utf-8")
        spec.write_text("spec v1", encoding="utf-8")
        manifest = self._write_manifest(
            [
                {
                    "id": "CONCEPT-SHADOW",
                    "kind": "concept",
                    "path": "docs/concept.md",
                    "status": "approved",
                    "upstream": [],
                    "github_issue": 1,
                },
                {
                    "id": "SPEC-CORE",
                    "kind": "spec",
                    "path": "docs/spec.md",
                    "status": "approved",
                    "upstream": ["CONCEPT-SHADOW"],
                    "github_issue": 2,
                },
            ]
        )
        artifacts = traceability.load_manifest(manifest)
        baseline = traceability.build_state(artifacts)

        concept.write_text("concept v2", encoding="utf-8")
        changed, affected = traceability.impact(artifacts, baseline)

        self.assertEqual(changed, ["CONCEPT-SHADOW"])
        self.assertEqual(affected, ["SPEC-CORE"])

    def test_rejects_cycles(self) -> None:
        manifest = self._write_manifest(
            [
                {
                    "id": "SPEC-ONE",
                    "kind": "spec",
                    "path": None,
                    "status": "draft",
                    "upstream": ["SPEC-TWO"],
                    "github_issue": None,
                },
                {
                    "id": "SPEC-TWO",
                    "kind": "spec",
                    "path": None,
                    "status": "draft",
                    "upstream": ["SPEC-ONE"],
                    "github_issue": None,
                },
            ]
        )

        with self.assertRaises(traceability.ManifestError):
            traceability.load_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
