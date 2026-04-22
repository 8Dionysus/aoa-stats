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


def test_catalog_profiles_expose_consumer_regrounding_inputs() -> None:
    module = load_build_views_module()
    receipts = module.load_receipts(
        [REPO_ROOT / "examples" / "session_harvest_family.receipts.example.json"]
    )
    outputs = module.build_all_views(receipts, ["session_harvest_family.receipts.example.json"])
    catalog = outputs["summary_surface_catalog.min.json"]

    for profile in catalog["surfaces"]:
        assert profile["owner_truth_inputs"]
        assert profile["authority_ceiling"].startswith("Weaker than ")
        assert profile["consumer_risk"] in {"low", "medium", "high"}
        assert profile["input_posture"]
        assert isinstance(profile["live_state_capable"], bool)

    surface_detection = next(
        profile for profile in catalog["surfaces"] if profile["name"] == "surface_detection_summary"
    )
    assert surface_detection["consumer_risk"] == "high"
    assert surface_detection["owner_truth_inputs"] == [
        "aoa-skills core skill application receipts"
    ]

    source_coverage = next(
        profile for profile in catalog["surfaces"] if profile["name"] == "source_coverage_summary"
    )
    assert source_coverage["input_posture"] == "registry_backed_coverage_audit"
    assert "config/live_receipt_sources.json" in source_coverage["owner_truth_inputs"]
    assert source_coverage["consumer_risk"] == "medium"


def test_source_coverage_thin_flags_prompt_regrounding_without_verdict_authority() -> None:
    module = load_build_views_module()
    receipts = module.load_receipts(
        [REPO_ROOT / "examples" / "session_harvest_family.receipts.example.json"]
    )
    outputs = module.build_all_views(receipts, ["session_harvest_family.receipts.example.json"])
    coverage = outputs["source_coverage_summary.min.json"]

    assert coverage["thin_signal_flags"] == [
        "missing_owner_repos",
        "unexpected_owner_repos",
        "owner_share_dominant",
    ]
    assert coverage["missing_owner_repos"] == [
        "aoa-memo",
        "aoa-playbooks",
        "aoa-techniques",
    ]
    assert coverage["unexpected_owner_repos"] == ["Dionysus"]

    prohibited_authority_fields = {
        "canonical_truth",
        "decision",
        "proof_passed",
        "recommended_route",
        "score",
        "verdict",
        "workflow_activation",
    }
    assert prohibited_authority_fields.isdisjoint(coverage)
