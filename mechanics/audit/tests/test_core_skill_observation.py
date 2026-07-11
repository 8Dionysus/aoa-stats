from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"
RECEIPT_FIXTURE = (
    REPO_ROOT
    / "stats"
    / "intake-contract"
    / "examples"
    / "session_harvest_family.receipts.example.json"
)
EXPECTED_COMMITTED_SHA256 = {
    "core_skill_application_summary.min.json": (
        "3c261eb42c1b2f87111a497551a53ec0efbf8427513f3b8d55fa79b61bb254a2"
    ),
    "surface_detection_summary.min.json": (
        "34588e56655b6df50e8144e8f188c7ec304d958151978839aa315e505b1ef202"
    ),
}

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import core_skill_observation  # noqa: E402


_MISSING = object()


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_root_facade_reexports_core_skill_observation_symbols() -> None:
    facade = load_build_views_module()

    assert (
        facade.build_core_skill_application_summary
        is core_skill_observation.build_core_skill_application_summary
    )
    assert (
        facade.build_surface_detection_summary
        is core_skill_observation.build_surface_detection_summary
    )
    assert facade.core_skill_identity is core_skill_observation.core_skill_identity
    assert (
        facade.surface_detection_context
        is core_skill_observation.surface_detection_context
    )


def core_skill_receipt(
    *,
    event_id: str,
    observed_at: str = "2026-04-06T20:20:00Z",
    event_kind: str = "core_skill_application_receipt",
    application_stage: str = "finish",
    kernel_id: str = "project-core-session-growth-v1",
    skill_name: str = "aoa-session-donor-harvest",
    detail_event_kind: Any = "harvest_packet_receipt",
    context: Any = _MISSING,
    evidence_ref_count: int = 1,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "kernel_id": kernel_id,
        "skill_name": skill_name,
        "application_stage": application_stage,
        "detail_event_kind": detail_event_kind,
    }
    if context is not _MISSING:
        payload["surface_detection_context"] = context
    return {
        "event_kind": event_kind,
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": f"run:{event_id}",
        "session_ref": f"session:{event_id}",
        "actor_ref": "aoa-skills:session-donor-harvest",
        "object_ref": {
            "repo": "aoa-skills",
            "kind": "skill",
            "id": skill_name,
            "version": "main",
        },
        "evidence_refs": [
            {"kind": "receipt", "ref": f"repo:aoa-skills/{event_id}/{index}"}
            for index in range(evidence_ref_count)
        ],
        "payload": payload,
    }


def generated_from(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "receipt_input_paths": [
            "stats/intake-contract/examples/"
            "session_harvest_family.receipts.example.json"
        ],
        "total_receipts": len(receipts),
        "latest_observed_at": max(
            receipt["observed_at"] for receipt in receipts
        ),
    }


def stable_json(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=False) + "\n").encode()


def test_finish_stage_selector_is_shared_and_preserves_input_order() -> None:
    first = core_skill_receipt(event_id="evt-finish-first")
    start = core_skill_receipt(
        event_id="evt-start", application_stage="start"
    )
    other_kind = core_skill_receipt(
        event_id="evt-other",
        event_kind="decision_fork_receipt",
    )
    second = core_skill_receipt(event_id="evt-finish-second")
    malformed = core_skill_receipt(event_id="evt-malformed")
    malformed["payload"] = []

    selected = core_skill_observation.finished_core_skill_application_receipts(
        [first, start, other_kind, second, malformed]
    )

    assert selected == [first, second]
    assert selected[0] is first
    assert selected[1] is second


@pytest.mark.parametrize(
    ("payload", "object_id", "expected"),
    (
        (
            {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
            },
            "object-fallback",
            (
                "project-core-session-growth-v1",
                "aoa-session-donor-harvest",
            ),
        ),
        (
            {"kernel_id": "project-core-session-growth-v1"},
            "object-fallback",
            ("unknown-kernel", "object-fallback"),
        ),
        (
            {"skill_name": "aoa-session-donor-harvest"},
            "object-fallback",
            ("unknown-kernel", "object-fallback"),
        ),
        ({}, "", ("unknown-kernel", "unknown-skill")),
    ),
)
def test_core_skill_identity_preserves_root_fallbacks(
    payload: dict[str, Any],
    object_id: str,
    expected: tuple[str, str],
) -> None:
    receipt = core_skill_receipt(event_id="evt-identity")
    receipt["payload"] = payload
    receipt["object_ref"]["id"] = object_id

    assert core_skill_observation.core_skill_identity(receipt) == expected


def test_surface_detection_context_accepts_only_nested_mapping() -> None:
    context = {
        "activation_truth": "manual-equivalent-adjacent",
        "candidate_counts": {"candidate_now": 1},
    }
    nested = core_skill_receipt(event_id="evt-context", context=context)
    missing = core_skill_receipt(event_id="evt-missing-context")
    non_mapping = core_skill_receipt(event_id="evt-list-context", context=[])

    assert core_skill_observation.surface_detection_context(nested) is context
    assert core_skill_observation.surface_detection_context(missing) == {}
    assert core_skill_observation.surface_detection_context(non_mapping) == {}


def test_core_skill_summary_preserves_grouping_latest_and_finish_filter() -> None:
    receipts = [
        core_skill_receipt(
            event_id="evt-latest",
            observed_at="2026-04-06T20:30:00Z",
            detail_event_kind="zeta_receipt",
        ),
        core_skill_receipt(
            event_id="evt-first",
            observed_at="2026-04-06T20:20:00Z",
            detail_event_kind="alpha_receipt",
        ),
        core_skill_receipt(
            event_id="evt-start",
            observed_at="2026-04-06T20:40:00Z",
            application_stage="start",
            detail_event_kind="ignored_receipt",
        ),
        core_skill_receipt(
            event_id="evt-empty-detail",
            observed_at="2026-04-06T20:25:00Z",
            detail_event_kind="",
        ),
    ]
    source = generated_from(receipts)

    summary = core_skill_observation.build_core_skill_application_summary(
        receipts, source
    )

    assert summary == {
        "schema_version": "aoa_stats_core_skill_application_summary_v1",
        "generated_from": source,
        "skills": [
            {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_count": 3,
                "latest_observed_at": "2026-04-06T20:30:00Z",
                "latest_session_ref": "session:evt-latest",
                "latest_run_ref": "run:evt-latest",
                "detail_event_kind_counts": {
                    "alpha_receipt": 1,
                    "zeta_receipt": 1,
                },
            }
        ],
    }


def test_surface_summary_preserves_advisory_counts_and_input_order_bounds() -> None:
    rich_context = {
        "activation_truth": "manual-equivalent-adjacent",
        "adjacent_owner_repos": ["aoa-techniques", "aoa-playbooks", ""],
        "owner_layer_ambiguity": True,
        "family_entry_refs": ["family:one", "", 7, "family:two"],
        "candidate_counts": {"candidate_now": 1, "candidate_later": 2},
        "suggested_handoff_targets": [
            "aoa-session-donor-harvest",
            "aoa-quest-harvest",
        ],
        "repeated_pattern_signal": True,
        "promotion_discussion_required": True,
    }
    receipts = [
        core_skill_receipt(
            event_id="evt-input-first",
            observed_at="2026-04-06T20:30:00Z",
            context=rich_context,
            evidence_ref_count=2,
        ),
        core_skill_receipt(
            event_id="evt-input-last",
            observed_at="2026-04-06T20:10:00Z",
            evidence_ref_count=1,
        ),
        core_skill_receipt(
            event_id="evt-start",
            observed_at="2026-04-06T20:40:00Z",
            application_stage="start",
            context=rich_context,
        ),
    ]
    source = generated_from(receipts)

    summary = core_skill_observation.build_surface_detection_summary(
        receipts, source
    )

    assert summary == {
        "schema_version": "aoa_stats_surface_detection_summary_v1",
        "generated_from": source,
        "windows": [
            {
                "window_id": "window:2026-04-06",
                "window_date": "2026-04-06",
                "core_skill_receipt_count": 2,
                "activated_count": 1,
                "manual_equivalent_adjacent_count": 1,
                "candidate_now_count": 1,
                "candidate_later_count": 2,
                "owner_layer_ambiguity_count": 1,
                "adjacent_owner_repo_counts": {
                    "aoa-playbooks": 1,
                    "aoa-techniques": 1,
                },
                "handoff_target_counts": {
                    "aoa-quest-harvest": 1,
                    "aoa-session-donor-harvest": 1,
                },
                "repeated_pattern_signal_count": 1,
                "promotion_discussion_count": 1,
                "family_entry_ref_count": 2,
                "evidence_ref_count": 3,
                "first_observed_at": "2026-04-06T20:30:00Z",
                "last_observed_at": "2026-04-06T20:10:00Z",
            }
        ],
    }


def test_projection_core_is_nonmutating_and_preserves_source_object() -> None:
    receipts = [
        core_skill_receipt(
            event_id="evt-nonmutating",
            context={"candidate_counts": {"candidate_now": 1}},
        )
    ]
    source = generated_from(receipts)
    original = deepcopy((receipts, source))

    core_summary = (
        core_skill_observation.build_core_skill_application_summary(
            receipts, source
        )
    )
    surface_summary = core_skill_observation.build_surface_detection_summary(
        receipts, source
    )

    assert (receipts, source) == original
    assert core_summary["generated_from"] is source
    assert surface_summary["generated_from"] is source


@pytest.mark.parametrize(
    ("output_name", "schema_name", "builder"),
    (
        (
            "core_skill_application_summary.min.json",
            "core-skill-application-summary.schema.json",
            core_skill_observation.build_core_skill_application_summary,
        ),
        (
            "surface_detection_summary.min.json",
            "surface-detection-summary.schema.json",
            core_skill_observation.build_surface_detection_summary,
        ),
    ),
)
def test_committed_outputs_preserve_bytes_and_schema(
    output_name: str,
    schema_name: str,
    builder,
) -> None:
    receipts = json.loads(RECEIPT_FIXTURE.read_text(encoding="utf-8"))
    source = generated_from(receipts)

    projected = builder(receipts, source)
    committed_bytes = (REPO_ROOT / "generated" / output_name).read_bytes()
    schema = json.loads(
        (REPO_ROOT / "schemas" / schema_name).read_text(encoding="utf-8")
    )

    assert stable_json(projected) == committed_bytes
    assert (
        hashlib.sha256(committed_bytes).hexdigest()
        == EXPECTED_COMMITTED_SHA256[output_name]
    )
    Draft202012Validator(schema).validate(projected)
