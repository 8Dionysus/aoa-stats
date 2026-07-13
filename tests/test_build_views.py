from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"
PROFILE_ROOT = REPO_ROOT / "stats" / "read-models" / "active"
RECEIPT_FIXTURE_REF = (
    "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
)


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def active_profile_output_names() -> tuple[str, ...]:
    profiles = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in PROFILE_ROOT.glob("*.profile.json")
    ]
    profiles.sort(key=lambda profile: profile["catalog_order"])
    return tuple(Path(profile["surface_ref"]).name for profile in profiles)


def test_build_all_views_fanout_matches_profiles_and_committed_bytes() -> None:
    module = load_build_views_module()
    receipts = module.load_receipts([REPO_ROOT / RECEIPT_FIXTURE_REF])

    outputs = module.build_all_views(receipts, [RECEIPT_FIXTURE_REF])
    active_output_names = active_profile_output_names()
    expected_output_names = (
        *active_output_names,
        "summary_surface_catalog.min.json",
    )

    assert set(outputs) == set(expected_output_names)
    for output_name in expected_output_names:
        committed = json.loads(
            (REPO_ROOT / "generated" / output_name).read_text(encoding="utf-8")
        )
        assert outputs[output_name] == committed, output_name

    catalog_output_names = tuple(
        Path(entry["surface_ref"]).name
        for entry in outputs["summary_surface_catalog.min.json"]["surfaces"]
    )
    assert catalog_output_names == active_output_names


def test_build_all_views_skips_missing_optional_sibling_surfaces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    receipts = module.load_receipts([REPO_ROOT / RECEIPT_FIXTURE_REF])
    for env_name in (
        "AOA_8DIONYSUS_ROOT",
        "AOA_SDK_ROOT",
        "AOA_AGENTS_ROOT",
        "AOA_PLAYBOOKS_ROOT",
        "AOA_MEMO_ROOT",
    ):
        monkeypatch.setenv(env_name, str(tmp_path / env_name.lower()))

    outputs = module.build_all_views(receipts, [RECEIPT_FIXTURE_REF])
    optional_output_names = {
        "codex_plane_deployment_summary.min.json",
        "codex_rollout_operations_summary.min.json",
        "codex_rollout_drift_summary.min.json",
        "rollout_campaign_summary.min.json",
        "drift_review_summary.min.json",
        "continuity_window_summary.min.json",
        "component_refresh_summary.min.json",
    }

    assert optional_output_names.isdisjoint(outputs)
    catalog_output_names = {
        Path(entry["surface_ref"]).name
        for entry in outputs["summary_surface_catalog.min.json"]["surfaces"]
    }
    assert optional_output_names.isdisjoint(catalog_output_names)


def test_build_all_views_uses_active_receipt_count_after_supersedes() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-0001",
            "observed_at": "2026-04-06T13:00:00Z",
            "run_ref": "run-001",
            "session_ref": "session:test-active-count",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
            },
            "evidence_refs": [{"kind": "receipt", "ref": "tmp/a.json"}],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "finish",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "tmp/a.json",
            },
        },
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-0002",
            "observed_at": "2026-04-06T13:01:00Z",
            "run_ref": "run-002",
            "session_ref": "session:test-active-count",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
            },
            "evidence_refs": [{"kind": "receipt", "ref": "tmp/b.json"}],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "finish",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "tmp/b.json",
            },
            "supersedes": "evt-core-0001",
        },
    ]

    outputs = module.build_all_views(receipts, ["memory"])
    catalog_generated_from = outputs["summary_surface_catalog.min.json"][
        "generated_from"
    ]

    assert catalog_generated_from["total_receipts"] == 1
