from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]


def load_part_json(relative_path: str) -> object:
    return json.loads((PART_ROOT / relative_path).read_text(encoding="utf-8"))


def load_repo_json(relative_path: str) -> object:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def test_component_refresh_summary_docs_are_discoverable_and_bounded() -> None:
    package_readme = (PART_ROOT.parents[1] / "README.md").read_text(encoding="utf-8")
    parts_index = (PART_ROOT.parents[1] / "PARTS.md").read_text(encoding="utf-8")
    part_readme = (PART_ROOT / "README.md").read_text(encoding="utf-8")
    architecture = (REPO_ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
    guide = (PART_ROOT / "docs" / "COMPONENT_REFRESH_SUMMARIES.md").read_text(encoding="utf-8")

    assert "parts/component-refresh/" in package_readme
    assert "component-refresh" in parts_index
    assert "docs/COMPONENT_REFRESH_SUMMARIES.md" in part_readme
    assert "component_refresh_summary.min.json" in architecture

    for token in (
        "derived-only stats view",
        "The summary may describe refresh posture. It does not become refresh truth.",
        "Do not treat this summary as proof that a refresh succeeded.",
        "Do not let stats overrule owner-local validation, receipts, or rollback",
    ):
        assert token in guide


def test_component_refresh_summary_example_and_schema_validate() -> None:
    schema = load_repo_json("schemas/component-refresh-summary.schema.json")
    example = load_part_json("examples/component_refresh_summary.example.json")

    assert isinstance(schema, dict)
    assert isinstance(example, dict)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(example)


def test_summary_refresh_law_example_tracks_live_stats_surfaces() -> None:
    payload = load_part_json("examples/summary_refresh_law.example.json")
    assert isinstance(payload, dict)

    assert payload["schema_version"] == "aoa_component_refresh_law_v1"
    assert payload["component_ref"] == "component:stats-derived-summaries:growth-refinery"
    assert payload["owner_repo"] == "aoa-stats"
    assert payload["followthrough_home"] == "aoa-playbooks:component-refresh-cycle"

    for relative_path in (
        "mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json",
        "scripts/build_views.py",
        "mechanics/recurrence/parts/component-refresh/docs/COMPONENT_REFRESH_SUMMARIES.md",
        "tests/test_build_views.py",
        "generated/candidate_lineage_summary.min.json",
        "generated/component_refresh_summary.min.json",
    ):
        assert (REPO_ROOT / relative_path).exists(), relative_path
