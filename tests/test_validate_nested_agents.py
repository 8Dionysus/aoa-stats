from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_nested_agents.py"
REPO_ROOT = SCRIPT_PATH.parents[1]
SPEC = importlib.util.spec_from_file_location("validate_nested_agents", SCRIPT_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

EXPECTED_PACK3_DOCS = {
    "examples/AGENTS.md",
    "generated/AGENTS.md",
    "schemas/AGENTS.md",
    "scripts/AGENTS.md",
    "src/AGENTS.md",
    "tests/AGENTS.md",
}

EXPECTED_CROSS_TOPOLOGY_DOCS = {
    "mechanics/AGENTS.md",
    "mechanics/recurrence/parts/live-receipt-refresh/config/AGENTS.md",
    "mechanics/recurrence/parts/live-receipt-refresh/systemd/AGENTS.md",
    "stats/AGENTS.md",
    "stats/intake-contract/AGENTS.md",
    "stats/measurement-contract/AGENTS.md",
    "stats/federation/AGENTS.md",
    "stats/operation-contracts/AGENTS.md",
    "stats/read-models/AGENTS.md",
    "stats/surface-catalog/AGENTS.md",
}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_minimal_required_tree(repo_root: Path) -> None:
    _write(repo_root / "AGENTS.md", "# AGENTS.md\nRoot guidance.\n")
    _write(repo_root / "mechanics/topology.json", '{"active_packages": []}\n')
    for rel_path, snippets in validator.REQUIRED_AGENTS_DOCS.items():
        _write(repo_root / rel_path, "# AGENTS.md\n" + "\n".join(snippets) + "\n")


class ValidateNestedAgentsTests(unittest.TestCase):
    def test_pack3_surface_map_is_required(self) -> None:
        self.assertTrue(EXPECTED_PACK3_DOCS.issubset(set(validator.REQUIRED_AGENTS_DOCS)))

    def test_cross_topology_surface_map_is_required(self) -> None:
        self.assertTrue(
            EXPECTED_CROSS_TOPOLOGY_DOCS.issubset(set(validator.REQUIRED_AGENTS_DOCS))
        )

    def test_live_topology_agent_map_is_derived(self) -> None:
        expected, issues = validator.discover_topology_agents(REPO_ROOT)
        self.assertEqual([], issues)
        self.assertIn("mechanics/agon/AGENTS.md", expected)
        self.assertIn("mechanics/experience/parts/AGENTS.md", expected)
        self.assertIn("mechanics/agon/legacy/AGENTS.md", expected)

    def test_live_repository_has_no_untracked_nested_agents(self) -> None:
        result = validator.validate(REPO_ROOT, fail_on_untracked=True)
        self.assertEqual((), result.issues)

    def test_minimal_required_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_minimal_required_tree(repo_root)
            result = validator.validate(repo_root)
            self.assertEqual((), result.issues)

    def test_missing_root_agents_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = validator.validate(Path(tmp))
            self.assertIn("AGENTS.md: root guidance file is missing", result.issues)

    def test_missing_required_doc_fails(self) -> None:
        first_rel = next(iter(validator.REQUIRED_AGENTS_DOCS))
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_minimal_required_tree(repo_root)
            (repo_root / first_rel).unlink()
            result = validator.validate(repo_root)
            self.assertTrue(any(first_rel in issue for issue in result.issues))

    def test_missing_required_snippet_fails(self) -> None:
        first_rel = next(iter(validator.REQUIRED_AGENTS_DOCS))
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_minimal_required_tree(repo_root)
            _write(repo_root / first_rel, "# AGENTS.md\nToo thin.\n")
            result = validator.validate(repo_root)
            self.assertTrue(any(first_rel in issue and "missing required snippet" in issue for issue in result.issues))

    def test_untracked_nested_agents_can_be_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_minimal_required_tree(repo_root)
            _write(repo_root / "extra" / "AGENTS.md", "# AGENTS.md\nExtra.\n")
            result = validator.validate(repo_root, fail_on_untracked=True)
            self.assertTrue(any("untracked nested AGENTS.md" in issue for issue in result.issues))

    def test_external_dependency_agents_are_outside_repo_guidance_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_minimal_required_tree(repo_root)
            _write(
                repo_root / ".deps" / "aoa-agents" / "AGENTS.md",
                "# AGENTS.md\nExternal dependency guidance.\n",
            )

            result = validator.validate(repo_root, fail_on_untracked=True)

            self.assertEqual((), result.issues)

    def test_advisory_can_become_strict(self) -> None:
        if not validator.ADVISORY_AGENT_DIRS:
            self.skipTest("repository has no advisory AGENTS.md candidates")
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_minimal_required_tree(repo_root)
            (repo_root / validator.ADVISORY_AGENT_DIRS[0]).mkdir(parents=True, exist_ok=True)
            result = validator.validate(repo_root, strict_advisory=True)
            self.assertTrue(any("high-risk directory" in issue for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
