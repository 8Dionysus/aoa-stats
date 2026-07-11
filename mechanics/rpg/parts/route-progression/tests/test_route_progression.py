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


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
BUILD_VIEWS_PATH = REPO_ROOT / "scripts" / "build_views.py"
RECEIPT_FIXTURE_REF = (
    "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
)
RECEIPT_FIXTURE_PATH = REPO_ROOT / RECEIPT_FIXTURE_REF
EXPECTED_COMMITTED_SHA256 = (
    "b992bfb216899b035b072b9ea57d0301384d06f5795e80210ff31e5b78ab9e30"
)

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import route_progression  # noqa: E402
from aoa_stats_builder.receipt_abi import (  # noqa: E402
    generated_from,
    load_receipts,
    resolve_active_receipts,
)


_MISSING = object()


def public_source(total_receipts: int = 1) -> dict[str, Any]:
    return {
        "receipt_input_paths": ["memory"],
        "total_receipts": total_receipts,
        "latest_observed_at": "2026-04-06T13:00:00Z",
    }


def assert_public_schema_valid(summary: dict[str, Any]) -> None:
    schema = json.loads(
        (REPO_ROOT / "schemas" / "route-progression-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(summary)


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", BUILD_VIEWS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def progression_receipt(
    event_id: str,
    observed_at: str,
    *,
    event_kind: str = "progression_delta_receipt",
    route_ref: Any = _MISSING,
    session_ref: str | None = None,
    verdict: Any = _MISSING,
    axis_deltas: Any = _MISSING,
    axis_delta_summary: Any = _MISSING,
    cautions: Any = _MISSING,
    evidence_count: int = 0,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if route_ref is not _MISSING:
        payload["route_ref"] = route_ref
    if verdict is not _MISSING:
        payload["verdict"] = verdict
    if axis_deltas is not _MISSING:
        payload["axis_deltas"] = axis_deltas
    if axis_delta_summary is not _MISSING:
        payload["axis_delta_summary"] = axis_delta_summary
    if cautions is not _MISSING:
        payload["cautions"] = cautions
    return {
        "event_kind": event_kind,
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": f"run:{event_id}",
        "session_ref": session_ref or f"session:{event_id}",
        "actor_ref": "aoa-skills:session-progression-lift",
        "object_ref": {
            "repo": "aoa-skills",
            "kind": "route_progression",
            "id": event_id,
            "version": "main",
        },
        "evidence_refs": [
            {"kind": "test", "ref": f"evidence:{event_id}:{index}"}
            for index in range(evidence_count)
        ],
        "payload": payload,
    }


def test_axis_vocabulary_and_template_preserve_exact_order() -> None:
    assert route_progression.AXES == (
        "boundary_integrity",
        "execution_reliability",
        "change_legibility",
        "review_sharpness",
        "proof_discipline",
        "provenance_hygiene",
        "deep_readiness",
    )

    first = route_progression.axis_template()
    second = route_progression.axis_template()

    assert tuple(first) == route_progression.AXES
    assert list(first.values()) == [0, 0, 0, 0, 0, 0, 0]
    first["boundary_integrity"] = 4
    assert second["boundary_integrity"] == 0

    schema = json.loads(
        (REPO_ROOT / "schemas" / "route-progression-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert tuple(schema["$defs"]["axis_deltas"]["required"]) == (route_progression.AXES)


@pytest.mark.parametrize("route_ref", (_MISSING, "", None, 0, False))
def test_falsey_or_missing_route_ref_falls_back_to_session(route_ref: Any) -> None:
    receipt = progression_receipt(
        "evt-fallback",
        "2026-04-06T12:00:00Z",
        route_ref=route_ref,
        session_ref="session:fallback-route",
    )

    summary = route_progression.build_route_progression_summary(
        [receipt], public_source()
    )

    assert summary["routes"][0]["route_ref"] == "session:fallback-route"
    assert_public_schema_valid(summary)


def test_latest_uses_timestamp_then_event_id_with_valid_verdict() -> None:
    receipts = [
        progression_receipt(
            "evt-latest-a",
            "2026-04-06T12:30:00Z",
            route_ref="route:latest",
            verdict="advance",
        ),
        progression_receipt(
            "evt-older-z",
            "2026-04-06T12:00:00Z",
            route_ref="route:latest",
            verdict="hold",
        ),
        progression_receipt(
            "evt-latest-z",
            "2026-04-06T12:30:00Z",
            route_ref="route:latest",
            verdict="reanchor",
        ),
    ]

    summary = route_progression.build_route_progression_summary(
        receipts, public_source(total_receipts=len(receipts))
    )
    route = summary["routes"][0]

    assert route["latest_observed_at"] == "2026-04-06T12:30:00Z"
    assert route["latest_verdict"] == "reanchor"
    assert_public_schema_valid(summary)


@pytest.mark.parametrize(
    "verdict",
    (_MISSING, None, "", 0, False, [], {}),
    ids=("missing", "none", "empty", "integer", "boolean", "list", "mapping"),
)
def test_invalid_or_missing_latest_verdict_normalizes_to_unknown(verdict: Any) -> None:
    receipt = progression_receipt(
        "evt-invalid-verdict",
        "2026-04-06T13:00:00Z",
        route_ref="route:invalid-verdict",
        verdict=verdict,
    )

    summary = route_progression.build_route_progression_summary(
        [receipt], public_source()
    )

    assert summary["routes"][0]["latest_verdict"] == "unknown"
    assert_public_schema_valid(summary)


@pytest.mark.parametrize(
    "axis_deltas",
    (
        _MISSING,
        {},
        {"boundary_integrity": "advance"},
        ["boundary_integrity"],
    ),
    ids=("missing", "empty", "semantic-values", "not-a-mapping"),
)
def test_current_semantic_axis_summary_without_numeric_legacy_deltas_fails(
    axis_deltas: Any,
) -> None:
    receipt = progression_receipt(
        "evt-semantic-only",
        "2026-04-06T13:00:00Z",
        verdict="advance",
        axis_deltas=axis_deltas,
        axis_delta_summary={"boundary_integrity": "advance"},
    )

    with pytest.raises(
        route_progression.RouteProgressionContractError,
        match=r"evt-semantic-only.*axis_delta_summary.*numeric axis_deltas",
    ):
        route_progression.build_route_progression_summary([receipt], public_source())


def test_hybrid_semantic_and_numeric_legacy_receipt_uses_numeric_deltas() -> None:
    receipt = progression_receipt(
        "evt-hybrid",
        "2026-04-06T13:00:00Z",
        route_ref="route:hybrid",
        verdict="advance",
        axis_deltas={"boundary_integrity": 2, "proof_discipline": -1},
        axis_delta_summary={
            "boundary_integrity": "advance",
            "proof_discipline": "hold",
        },
        cautions=["legacy numeric path retained"],
    )

    summary = route_progression.build_route_progression_summary(
        [receipt], public_source()
    )

    assert summary["routes"][0]["cumulative_axis_deltas"] == {
        "boundary_integrity": 2,
        "execution_reliability": 0,
        "change_legibility": 0,
        "review_sharpness": 0,
        "proof_discipline": -1,
        "provenance_hygiene": 0,
        "deep_readiness": 0,
    }
    assert summary["routes"][0]["caution_count"] == 1
    assert_public_schema_valid(summary)


def test_aggregation_preserves_int_bool_caution_and_evidence_semantics() -> None:
    receipts = [
        progression_receipt(
            "evt-z-1",
            "2026-04-06T12:00:00Z",
            route_ref="route:z",
            axis_deltas={
                "boundary_integrity": True,
                "execution_reliability": False,
                "change_legibility": 2,
                "review_sharpness": 1.5,
                "unknown_axis": 99,
            },
            cautions=["review", "", None],
            evidence_count=2,
        ),
        progression_receipt(
            "evt-z-2",
            "2026-04-06T12:10:00Z",
            route_ref="route:z",
            axis_deltas={
                "boundary_integrity": -2,
                "execution_reliability": "3",
                "proof_discipline": 1,
                "deep_readiness": None,
            },
            cautions="not-a-list",
            evidence_count=1,
        ),
        progression_receipt(
            "evt-a",
            "2026-04-06T12:20:00Z",
            route_ref="route:a",
            axis_deltas=["not-a-mapping"],
            cautions=[],
            evidence_count=4,
        ),
    ]

    summary = route_progression.build_route_progression_summary(
        receipts, public_source(total_receipts=len(receipts))
    )
    routes = summary["routes"]

    assert [route["route_ref"] for route in routes] == ["route:a", "route:z"]
    assert routes[0]["cumulative_axis_deltas"] == {
        "boundary_integrity": 0,
        "execution_reliability": 0,
        "change_legibility": 0,
        "review_sharpness": 0,
        "proof_discipline": 0,
        "provenance_hygiene": 0,
        "deep_readiness": 0,
    }
    assert routes[0]["evidence_ref_count"] == 4
    assert routes[1]["total_progression_receipts"] == 2
    assert routes[1]["cumulative_axis_deltas"] == {
        "boundary_integrity": -1,
        "execution_reliability": 0,
        "change_legibility": 2,
        "review_sharpness": 0,
        "proof_discipline": 1,
        "provenance_hygiene": 0,
        "deep_readiness": 0,
    }
    assert routes[1]["caution_count"] == 3
    assert routes[1]["evidence_ref_count"] == 3
    assert_public_schema_valid(summary)


def test_empty_and_non_target_inputs_publish_an_empty_bounded_view() -> None:
    source = public_source()
    non_target = progression_receipt(
        "evt-other",
        "2026-04-06T12:00:00Z",
        event_kind="decision_fork_receipt",
        route_ref="route:ignored",
    )

    empty_summary = route_progression.build_route_progression_summary([], source)
    assert empty_summary == {
        "schema_version": "aoa_stats_route_progression_summary_v1",
        "generated_from": source,
        "routes": [],
    }
    non_target_summary = route_progression.build_route_progression_summary(
        [non_target], source
    )
    assert non_target_summary["routes"] == []
    assert_public_schema_valid(empty_summary)
    assert_public_schema_valid(non_target_summary)


def test_projection_is_nonmutating_and_preserves_source_identity() -> None:
    receipts = [
        progression_receipt(
            "evt-pure",
            "2026-04-06T12:00:00Z",
            route_ref="route:pure",
            axis_deltas={"change_legibility": 1},
            cautions=["bounded"],
        )
    ]
    source = public_source()
    original = deepcopy((receipts, source))

    projected = route_progression.build_route_progression_summary(receipts, source)

    assert (receipts, source) == original
    assert projected["generated_from"] is source
    assert_public_schema_valid(projected)


def test_core_matches_root_schema_and_committed_bytes() -> None:
    facade = load_build_views_module()
    receipts = load_receipts([RECEIPT_FIXTURE_PATH])
    active_receipts = resolve_active_receipts(receipts)
    source = generated_from(active_receipts, [RECEIPT_FIXTURE_REF])

    projected = route_progression.build_route_progression_summary(
        active_receipts, source
    )
    root_projected = facade.build_route_progression_summary(active_receipts, source)
    committed_bytes = (
        REPO_ROOT / "generated" / "route_progression_summary.min.json"
    ).read_bytes()
    assert facade.AXES is route_progression.AXES
    assert facade.axis_template is route_progression.axis_template
    assert (
        facade.build_route_progression_summary
        is route_progression.build_route_progression_summary
    )
    assert projected == root_projected
    assert facade.stable_json(projected).encode() == committed_bytes
    assert hashlib.sha256(committed_bytes).hexdigest() == EXPECTED_COMMITTED_SHA256
    assert_public_schema_valid(projected)
