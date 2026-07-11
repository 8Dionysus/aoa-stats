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
    "2f3b958e75099e8ae0a3035eca60be7b8809cf2f6950fdfaa2f934ab1845649c"
)

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import runtime_closeout  # noqa: E402
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


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", BUILD_VIEWS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def closeout_receipt(
    event_id: str,
    observed_at: str,
    *,
    event_kind: str = runtime_closeout.RUNTIME_CLOSEOUT_EVENT_KIND,
    program_id: Any = "program-v1",
    wave_id: Any = "W1",
    object_id: str = "program-v1:W1",
    session_ref: str | None = None,
    gate_result: Any = "pass",
    handoff_status: Any = "submitted",
    audit_only: Any = True,
    case_count: Any = 2,
    next_action: Any = "review-complete",
    truth_status: Any = _MISSING,
    evidence_count: int = 1,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "program_id": program_id,
        "wave_id": wave_id,
        "gate_result": gate_result,
        "reviewed_closeout_handoff_status": handoff_status,
        "reviewed_closeout_audit_only": audit_only,
        "case_count": case_count,
        "next_action": next_action,
    }
    if truth_status is _MISSING:
        payload["truth_status"] = {
            "source_authored": True,
            "deployed": True,
            "trial_proven": True,
            "live_available": True,
        }
    else:
        payload["truth_status"] = truth_status
    return {
        "event_kind": event_kind,
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": f"run:{event_id}",
        "session_ref": session_ref or f"session:{event_id}",
        "actor_ref": "abyss-stack:aoa-local-ai-trials",
        "object_ref": {
            "repo": "abyss-stack",
            "kind": "runtime_wave_closeout",
            "id": object_id,
            "version": "runtime",
        },
        "evidence_refs": [
            {"kind": "test", "ref": f"evidence:{event_id}:{index}"}
            for index in range(evidence_count)
        ],
        "payload": payload,
    }


def assert_public_schema_valid(summary: dict[str, Any]) -> None:
    schema = json.loads(
        (REPO_ROOT / "schemas" / "runtime-closeout-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(summary)


def test_identity_prefers_complete_payload_pair() -> None:
    receipt = closeout_receipt(
        "evt-payload-identity",
        "2026-04-06T12:00:00Z",
        program_id="payload-program",
        wave_id="payload-wave",
        object_id="object-program:object-wave",
    )

    assert runtime_closeout.runtime_closeout_identity(receipt) == (
        "payload-program",
        "payload-wave",
    )


@pytest.mark.parametrize(
    ("program_id", "wave_id", "object_id", "expected"),
    (
        ("payload-program", "", "object-program:object-wave", ("object-program", "object-wave")),
        (None, "payload-wave", "family:program:W2", ("family:program", "W2")),
        (0, False, ":W3", ("unknown-program", "W3")),
        ([], {}, "program-v2:", ("program-v2", "unknown-wave")),
    ),
    ids=("partial-payload", "last-colon", "missing-program", "missing-wave"),
)
def test_identity_falls_back_to_last_colon_object_pair(
    program_id: Any,
    wave_id: Any,
    object_id: str,
    expected: tuple[str, str],
) -> None:
    receipt = closeout_receipt(
        "evt-object-identity",
        "2026-04-06T12:00:00Z",
        program_id=program_id,
        wave_id=wave_id,
        object_id=object_id,
    )

    assert runtime_closeout.runtime_closeout_identity(receipt) == expected


def test_identity_without_object_pair_uses_session_as_wave() -> None:
    receipt = closeout_receipt(
        "evt-session-identity",
        "2026-04-06T12:00:00Z",
        program_id="",
        wave_id=None,
        object_id="unpaired-object",
        session_ref="session:runtime-fallback",
    )

    assert runtime_closeout.runtime_closeout_identity(receipt) == (
        "unknown-program",
        "session:runtime-fallback",
    )


def test_only_historical_wave_kind_is_admitted_without_implicit_aliasing() -> None:
    receipts = [
        closeout_receipt(
            "evt-trial",
            "2026-04-06T12:00:00Z",
            event_kind="runtime_trial_closeout_receipt",
        ),
        closeout_receipt(
            "evt-return",
            "2026-04-06T12:01:00Z",
            event_kind="runtime_return_closeout_receipt",
        ),
        closeout_receipt(
            "evt-unrelated",
            "2026-04-06T12:02:00Z",
            event_kind="eval_result_receipt",
        ),
    ]
    source = public_source(total_receipts=3)
    original_receipts = deepcopy(receipts)
    original_source = deepcopy(source)

    summary = runtime_closeout.build_runtime_closeout_summary(receipts, source)

    assert summary == {
        "schema_version": "aoa_stats_runtime_closeout_summary_v1",
        "generated_from": source,
        "closeouts": [],
    }
    assert summary["generated_from"] is source
    assert receipts == original_receipts
    assert source == original_source


def test_grouping_sorting_latest_tie_break_counts_and_evidence_are_stable() -> None:
    receipts = [
        closeout_receipt(
            "evt-z-first-input",
            "2026-04-06T13:00:00Z",
            program_id="z-program",
            wave_id="W2",
            gate_result="hold",
            handoff_status="pending",
            evidence_count=2,
        ),
        closeout_receipt(
            "evt-a",
            "2026-04-06T12:00:00Z",
            program_id="a-program",
            wave_id="W1",
            evidence_count=0,
        ),
        closeout_receipt(
            "evt-z-latest-a",
            "2026-04-06T14:00:00Z",
            program_id="z-program",
            wave_id="W2",
            gate_result="pass",
            handoff_status="submitted",
            audit_only=False,
            case_count="3",
            next_action="continue",
            evidence_count=1,
        ),
        closeout_receipt(
            "evt-z-latest-z",
            "2026-04-06T14:00:00Z",
            program_id="z-program",
            wave_id="W2",
            gate_result="fail",
            handoff_status="reviewed",
            audit_only=True,
            case_count=4,
            next_action="reanchor",
            truth_status={"source_authored": True, "deployed": False},
            evidence_count=3,
        ),
    ]

    summary = runtime_closeout.build_runtime_closeout_summary(
        receipts, public_source(total_receipts=len(receipts))
    )

    assert [(row["program_id"], row["wave_id"]) for row in summary["closeouts"]] == [
        ("a-program", "W1"),
        ("z-program", "W2"),
    ]
    closeout = summary["closeouts"][1]
    assert closeout["closeout_receipt_count"] == 3
    assert closeout["latest_gate_result"] == "fail"
    assert closeout["gate_result_counts"] == {"fail": 1, "hold": 1, "pass": 1}
    assert closeout["latest_reviewed_closeout_handoff_status"] == "reviewed"
    assert closeout["reviewed_closeout_handoff_status_counts"] == {
        "pending": 1,
        "reviewed": 1,
        "submitted": 1,
    }
    assert closeout["latest_reviewed_closeout_audit_only"] is True
    assert closeout["latest_case_count"] == 4
    assert closeout["latest_next_action"] == "reanchor"
    assert closeout["latest_truth_status"] == {
        "source_authored": True,
        "deployed": False,
        "trial_proven": False,
        "live_available": False,
    }
    assert closeout["first_observed_at"] == "2026-04-06T13:00:00Z"
    assert closeout["last_observed_at"] == "2026-04-06T14:00:00Z"
    assert closeout["evidence_ref_count"] == 6
    assert_public_schema_valid(summary)


def test_first_observed_retains_input_order_compatibility_semantics() -> None:
    later_first = closeout_receipt(
        "evt-later-input-first",
        "2026-04-06T15:00:00Z",
    )
    earlier_second = closeout_receipt(
        "evt-earlier-input-second",
        "2026-04-06T10:00:00Z",
    )

    forward = runtime_closeout.build_runtime_closeout_summary(
        [later_first, earlier_second], public_source(total_receipts=2)
    )
    reverse = runtime_closeout.build_runtime_closeout_summary(
        [earlier_second, later_first], public_source(total_receipts=2)
    )

    assert forward["closeouts"][0]["first_observed_at"] == "2026-04-06T15:00:00Z"
    assert reverse["closeouts"][0]["first_observed_at"] == "2026-04-06T10:00:00Z"
    assert forward["closeouts"][0]["last_observed_at"] == "2026-04-06T15:00:00Z"
    assert reverse["closeouts"][0]["last_observed_at"] == "2026-04-06T15:00:00Z"


def test_falsey_defaults_and_non_mapping_truth_status_preserve_legacy_coercion() -> None:
    receipt = closeout_receipt(
        "evt-defaults",
        "2026-04-06T13:00:00Z",
        gate_result="",
        handoff_status=None,
        audit_only=0,
        case_count="",
        next_action=False,
        truth_status=["not", "a", "mapping"],
    )

    closeout = runtime_closeout.build_runtime_closeout_summary(
        [receipt], public_source()
    )["closeouts"][0]

    assert closeout["latest_gate_result"] == "unknown"
    assert closeout["gate_result_counts"] == {"unknown": 1}
    assert closeout["latest_reviewed_closeout_handoff_status"] == "unknown"
    assert closeout["reviewed_closeout_handoff_status_counts"] == {"unknown": 1}
    assert closeout["latest_reviewed_closeout_audit_only"] is False
    assert closeout["latest_case_count"] == 0
    assert closeout["latest_next_action"] == "unspecified"
    assert closeout["latest_truth_status"] == {
        "source_authored": False,
        "deployed": False,
        "trial_proven": False,
        "live_available": False,
    }
    assert_public_schema_valid(
        runtime_closeout.build_runtime_closeout_summary([receipt], public_source())
    )


def test_truthy_numeric_string_case_count_uses_legacy_integer_coercion() -> None:
    receipt = closeout_receipt(
        "evt-string-case-count",
        "2026-04-06T13:00:00Z",
        case_count="3",
    )

    closeout = runtime_closeout.build_runtime_closeout_summary(
        [receipt], public_source()
    )["closeouts"][0]

    assert closeout["latest_case_count"] == 3


def test_projection_preserves_root_alias_schema_committed_bytes_hash_and_inputs() -> None:
    receipts = load_receipts([RECEIPT_FIXTURE_PATH])
    active_receipts = resolve_active_receipts(receipts)
    source = generated_from(active_receipts, [RECEIPT_FIXTURE_REF])
    original_receipts = deepcopy(active_receipts)
    original_source = deepcopy(source)
    facade = load_build_views_module()

    projected = runtime_closeout.build_runtime_closeout_summary(
        active_receipts, source
    )
    committed = (
        REPO_ROOT / "generated" / "runtime_closeout_summary.min.json"
    ).read_bytes()

    assert facade.runtime_closeout_identity is runtime_closeout.runtime_closeout_identity
    assert (
        facade.build_runtime_closeout_summary
        is runtime_closeout.build_runtime_closeout_summary
    )
    assert projected == facade.build_runtime_closeout_summary(active_receipts, source)
    assert_public_schema_valid(projected)
    assert facade.stable_json(projected).encode() == committed
    assert hashlib.sha256(committed).hexdigest() == EXPECTED_COMMITTED_SHA256
    assert active_receipts == original_receipts
    assert source == original_source
