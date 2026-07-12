from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.surface_catalog import public_surface_profiles  # noqa: E402


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_summary_surface_catalog_contract_is_exact() -> None:
    module = load_build_views_module()
    receipts = module.load_receipts(
        [
            REPO_ROOT
            / "stats"
            / "intake-contract"
            / "examples"
            / "session_harvest_family.receipts.example.json"
        ]
    )
    outputs = module.build_all_views(
        receipts,
        ["stats/intake-contract/examples/session_harvest_family.receipts.example.json"],
    )
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
        "consumer_expectation": "consumers verify schema_version, generated_from, validation_refs, surface strength refs, owner truth inputs, deferred activation gaps, and build_views --check before using catalog entries as observability hints",
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
    assert payload["surface_strength_model_ref"] == (
        "stats/surface-catalog/SURFACE_STRENGTH_MODEL.md"
    )
    assert (REPO_ROOT / payload["surface_strength_model_ref"]).is_file()
    assert payload["validation_refs"] == [
        "scripts/build_views.py",
        "scripts/validate_repo.py",
        "tests/test_summary_surface_catalog.py",
    ]
    authored_active, authored_deferred = public_surface_profiles(
        REPO_ROOT / "stats" / "read-models"
    )
    available_output_names = set(outputs)
    expected_active = [
        profile
        for profile in authored_active
        if Path(profile["surface_ref"]).name in available_output_names
    ]
    assert payload["surfaces"] == expected_active
    assert payload["deferred_contract_surfaces"] == authored_deferred
    assert payload["surfaces"]
    assert all("surface_ref" in entry for entry in payload["surfaces"])
    assert all("input_posture" in entry for entry in payload["surfaces"])
    assert all("owner_truth_inputs" in entry for entry in payload["surfaces"])
    assert all("authority_ceiling" in entry for entry in payload["surfaces"])
    assert all("consumer_risk" in entry for entry in payload["surfaces"])
    assert all("live_state_capable" in entry for entry in payload["surfaces"])
    assert all("path" not in entry for entry in payload["surfaces"])
    assert all("catalog_order" not in entry for entry in payload["surfaces"])
    assert all("mechanic_routes" not in entry for entry in payload["surfaces"])


def test_surface_strength_vocabulary_matches_authored_profile_postures() -> None:
    model = (
        REPO_ROOT / "stats/surface-catalog/SURFACE_STRENGTH_MODEL.md"
    ).read_text(encoding="utf-8")
    posture_section = model.split("## Input posture classes", 1)[1].split(
        "## Consumer risk", 1
    )[0]
    documented_postures = set(
        re.findall(r"^- `([^`]+)`:", posture_section, re.MULTILINE)
    )
    active, deferred = public_surface_profiles(REPO_ROOT / "stats" / "read-models")
    authored_postures = {
        profile["input_posture"] for profile in [*active, *deferred]
    }

    assert documented_postures == authored_postures
    assert "antifragility_vector" not in model
    assert "Today" not in model


def test_consumer_regrounding_inputs_prefer_real_owner_surfaces() -> None:
    payload = json.loads(
        (REPO_ROOT / "generated" / "summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )
    profiles = {item["name"]: item for item in payload["surfaces"]}

    route_inputs = profiles["route_progression_summary"]["owner_truth_inputs"]
    assert route_inputs[:2] == [
        "aoa-skills/skills/core/session-growth/aoa-session-progression-lift/references/progression-delta-receipt-schema.yaml",
        "aoa-skills/mechanics/growth-cycle/examples/session-growth-artifacts/progression_delta_receipt.kernel-maturity.json",
    ]
    assert "legacy numeric" not in route_inputs[0]

    assert "owner_landing_summary" not in profiles

    stress_input = profiles["stress_recovery_window_summary"]["owner_truth_inputs"][0]
    assert stress_input.startswith("aoa-evals/")


def test_artifact_bundle_manifest_requires_registry_lifecycle_and_sbom_lite() -> None:
    manifest = json.loads(
        (
            REPO_ROOT
            / "manifests"
            / "artifact_bundles"
            / "summary_surface_catalog.bundle.json"
        ).read_text(encoding="utf-8")
    )

    assert manifest["artifact_class"] == "derived_observability_readmodel_catalog"
    assert manifest["public_safe"] is True
    assert (
        manifest["artifact_source"]["kind"]
        == "generated_observability_readmodel_catalog"
    )
    assert manifest["lifecycle"]["initial_state"] == "candidate"
    assert "release-ready" in manifest["lifecycle"]["promotion_path"]
    assert manifest["consumer_contract"]["registry_required"] is True
    command_text = "\n".join(manifest["consumer_command"])
    assert "evidence-promote" in command_text
    assert "materialize-subjects" in command_text
    assert "trust-gate" in command_text
    assert "registry-latest" in command_text
    assert "--consumer-ref aoa-stats:summary-surface-catalog" in command_text
    assert {item["role"] for item in manifest["artifact_subjects"]} == {
        "authority_doc",
        "schema",
        "summary_surface_catalog",
    }
    assert "--source-repo aoa-stats" in command_text
    assert "--trust-root-mode host_managed" in command_text
    assert manifest["consumer_contract"]["subject_store_required"] is True
    assert (
        manifest["consumer_contract"]["admission_gate"]
        == "fail_closed_consumer_admission"
    )
