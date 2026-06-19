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
        "artifact_identity",
        "surface_strength_model_ref",
        "generated_from",
        "validation_refs",
        "deferred_contract_surfaces",
        "surfaces",
    }
    assert payload["schema_version"] == "aoa_stats_summary_surface_catalog_v2"
    assert payload["schema_ref"] == "schemas/summary-surface-catalog.schema.json"
    assert payload["owner_repo"] == "aoa-stats"
    assert payload["surface_kind"] == "runtime_surface"
    assert payload["authority_ref"] == "docs/ARCHITECTURE.md"
    assert payload["artifact_identity"] == {
        "artifact_class": "derived_observability_readmodel_catalog",
        "surface_state": "public_generated_summary_surface_catalog",
        "owner_repo": "aoa-stats",
        "authority_ref": "docs/ARCHITECTURE.md",
        "producer": "scripts/build_views.py via aoa_stats_builder.surface_catalog from source-owned receipts and bounded examples",
        "consumer_expectation": "consumers verify schema_version, generated_from, validation_refs, surface strength refs, owner truth inputs, and build_views --check before using catalog entries as observability hints",
        "privacy_boundary": "public derived summary refs only; no raw private receipts, session captures, owner payload bodies, or runtime-local evidence",
        "content_identity": "generated/summary_surface_catalog.min.json rebuilt from the active receipt feed and compared by build_views --check",
        "abi_epoch": "aoa_stats_summary_surface_catalog_v2",
        "contract_version": "summary-surface-catalog.schema.json@aoa_stats_summary_surface_catalog_v2#artifact_identity",
        "trust_layer": ["abi_contract_signature", "w3c_prov_lineage"],
        "verification": [
            "python scripts/build_views.py --check",
            "python scripts/validate_repo.py",
            "python -m pytest -q tests/test_summary_surface_catalog.py",
        ],
        "action": "ADD_CONSUMER_EXPECTATION",
    }
    assert payload["surface_strength_model_ref"] == "docs/SURFACE_STRENGTH_MODEL.md"
    assert payload["validation_refs"] == [
        "scripts/build_views.py",
        "scripts/validate_repo.py",
        "tests/test_summary_surface_catalog.py",
    ]
    assert payload["deferred_contract_surfaces"] == [
        {
            "name": "antifragility_vector",
            "status": "contract_only",
            "contract_ref": "docs/ANTIFRAGILITY_VECTOR.md",
            "schema_ref": "schemas/antifragility_vector_v1.json",
            "activation_condition": "Activate only after one owner-linked repeated-window receipt family and bounded eval chain exist for the same stressor family.",
            "authority_ceiling": "Even after activation this surface stays weaker than owner-local stressor receipts and bounded eval reports.",
        }
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
        "codex_plane_deployment_summary",
        "codex_rollout_operations_summary",
        "codex_rollout_drift_summary",
        "rollout_campaign_summary",
        "drift_review_summary",
        "continuity_window_summary",
        "component_refresh_summary",
        "memory_movement_summary",
        "titan_incarnation_summary",
        "titan_summon_summary",
        "runtime_closeout_summary",
        "stress_recovery_window_summary",
        "source_coverage_summary",
        "surface_detection_summary",
    ]
    assert all("surface_ref" in entry for entry in payload["surfaces"])
    assert all("input_posture" in entry for entry in payload["surfaces"])
    assert all("owner_truth_inputs" in entry for entry in payload["surfaces"])
    assert all("authority_ceiling" in entry for entry in payload["surfaces"])
    assert all("consumer_risk" in entry for entry in payload["surfaces"])
    assert all("live_state_capable" in entry for entry in payload["surfaces"])
    assert all("path" not in entry for entry in payload["surfaces"])
