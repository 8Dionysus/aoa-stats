from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_summary_surface_catalog_contract_is_exact() -> None:
    module = load_build_views_module()
    receipts = module.load_receipts(
        [REPO_ROOT / "examples" / "session_harvest_family.receipts.example.json"]
    )
    outputs = module.build_all_views(receipts, ["session_harvest_family.receipts.example.json"])
    payload = outputs["summary_surface_catalog.min.json"]

    assert set(payload) == {
        "schema_version",
        "schema_ref",
        "owner_repo",
        "surface_kind",
        "authority_ref",
        "generated_from",
        "validation_refs",
        "surfaces",
    }
    assert payload["schema_version"] == "aoa_stats_summary_surface_catalog_v2"
    assert payload["schema_ref"] == "schemas/summary-surface-catalog.schema.json"
    assert payload["owner_repo"] == "aoa-stats"
    assert payload["surface_kind"] == "runtime_surface"
    assert payload["authority_ref"] == "docs/ARCHITECTURE.md"
    assert payload["validation_refs"] == [
        "scripts/build_views.py",
        "scripts/validate_repo.py",
        "tests/test_summary_surface_catalog.py",
    ]
    assert [entry["name"] for entry in payload["surfaces"]] == [
        "core_skill_application_summary",
        "object_summary",
        "candidate_lineage_summary",
        "owner_landing_summary",
        "supersession_drop_summary",
        "repeated_window_summary",
        "route_progression_summary",
        "fork_calibration_summary",
        "session_growth_branch_summary",
        "automation_pipeline_summary",
        "automation_followthrough_summary",
        "runtime_closeout_summary",
        "stress_recovery_window_summary",
        "surface_detection_summary",
    ]
    assert all("surface_ref" in entry for entry in payload["surfaces"])
    assert all("path" not in entry for entry in payload["surfaces"])
