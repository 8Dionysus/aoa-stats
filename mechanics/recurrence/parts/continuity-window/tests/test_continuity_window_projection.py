from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[5]
PART_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"
RECEIPT_FIXTURE = (
    REPO_ROOT
    / "stats"
    / "intake-contract"
    / "examples"
    / "session_harvest_family.receipts.example.json"
)
EXPECTED_COMMITTED_SHA256 = (
    "6038254ebb9e58f51fcc22ea5d439d2a6fa365292a951bab1238e5785bd9c6e9"
)
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import continuity_window  # noqa: E402
from aoa_stats_builder.continuity_window_sources import (  # noqa: E402
    ContinuityWindowInputBundle,
)


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def continuity_payload(*, status: str = "active") -> dict[str, Any]:
    return {
        "schema_version": "self_agency_continuity_window_v1",
        "continuity_ref": "CONT-test-01",
        "revision_window_ref": "REV-test-01",
        "reanchor_ref": "REA-test-01",
        "anchor_artifact_ref": "artifact:verification_result:test-01",
        "continuity_status": status,
        "agent_id": "AOA-A-0001",
        "role": "architect",
        "memory_scope": "workspace",
        "approval_mode": "required",
        "rollback_marker": "ROLL-test-01",
        "max_iterations": 3,
        "notes": "bounded reference",
    }


def memo_payload(
    *, timeline: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    return {
        "id": "prov.test-continuity",
        "title": "Test continuity provenance",
        "summary": "Bounded reference thread",
        "status": "active",
        "continuity_ref": "CONT-test-01",
        "revision_window_ref": "REV-test-01",
        "reanchor_ref": "REA-test-01",
        "anchor_artifact_ref": "artifact:verification_result:test-01",
        "writeback_target": "provenance_thread",
        "source_refs": [
            "repo:aoa-agents/examples/self_agent_checkpoint/"
            "self_agency_continuity_window.example.json",
            "repo:aoa-playbooks/playbooks/"
            "self-agency-continuity-cycle/PLAYBOOK.md",
            "repo:aoa-evals/bundles/"
            "aoa-continuity-anchor-integrity/EVAL.md",
            "repo:aoa-evals/bundles/"
            "aoa-self-reanchor-correctness/EVAL.md",
        ],
        "memory_object_ids": ["memo.state.test-continuity"],
        "timeline": timeline
        or [
            {
                "at": "2026-04-12T13:50:00Z",
                "action": "published the bounded continuity window",
            },
            {
                "at": "2026-04-12T14:20:00Z",
                "action": "captured the continuity provenance thread",
            },
        ],
    }


def playbook_text(
    *,
    playbook_id: str = "AOA-P-0029",
    status: str = "experimental",
    scenario: str = "self_agency_continuity_cycle",
    fallback_mode: str = "review_required",
    return_posture: str = "artifact_anchor",
    expected_artifacts: list[str] | None = None,
    return_anchor_artifacts: list[str] | None = None,
    eval_anchors: list[str] | None = None,
) -> str:
    list_fields = {
        "expected_artifacts": expected_artifacts
        or [
            "continuity_window",
            "reflective_revision_decision",
            "reanchor_decision",
            "anchor_trace",
            "continuity_writeback_record",
            "continuity_summary_refresh_record",
        ],
        "return_anchor_artifacts": return_anchor_artifacts
        or ["continuity_window", "reanchor_decision", "anchor_trace"],
        "eval_anchors": eval_anchors or list(continuity_window.CONTINUITY_EVAL_ANCHORS),
    }
    lines = [
        "---",
        f"id: {playbook_id}",
        "name: self-agency-continuity-cycle",
        f"status: {status}",
        f"scenario: {scenario}",
        f"fallback_mode: {fallback_mode}",
        f"return_posture: {return_posture}",
    ]
    for key, values in list_fields.items():
        lines.append(f"{key}:")
        lines.extend(f"  - {value}" for value in values)
    lines.extend(["---", "", "# self-agency-continuity-cycle", ""])
    return "\n".join(lines)


def eval_entries() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "eval_path": continuity_window.CONTINUITY_EVAL_PATHS[name],
            "claim_type": "bounded",
            "review_required": True,
            "status": "draft",
        }
        for name in continuity_window.CONTINUITY_EVAL_ANCHORS
    ]


def write_reference_tree(
    tmp_path: Path,
    *,
    continuity: dict[str, Any] | None = None,
    memo: dict[str, Any] | None = None,
    playbook: str | None = None,
    evals: list[dict[str, Any]] | None = None,
    eval_catalog_version: int = 1,
    legacy_memo_path: bool = False,
) -> dict[str, Path]:
    roots = {
        "AOA_AGENTS_ROOT": tmp_path / ".deps" / "aoa-agents",
        "AOA_PLAYBOOKS_ROOT": tmp_path / ".deps" / "aoa-playbooks",
        "AOA_MEMO_ROOT": tmp_path / ".deps" / "aoa-memo",
        "AOA_EVALS_ROOT": tmp_path / ".deps" / "aoa-evals",
    }
    continuity_path = (
        roots["AOA_AGENTS_ROOT"]
        / "mechanics/checkpoint/parts/continuity-lane/examples/"
        "self-agency-continuity-window.example.json"
    )
    playbook_path = (
        roots["AOA_PLAYBOOKS_ROOT"]
        / "playbooks/continuity/session-growth/self-agency-continuity-cycle/PLAYBOOK.md"
    )
    memo_relative = (
        "mechanics/writeback/examples/"
        "provenance_thread.self-agency-continuity.example.json"
        if legacy_memo_path
        else "mechanics/writeback/parts/growth-and-continuity/examples/"
        "provenance_thread.self-agency-continuity.example.json"
    )
    memo_path = roots["AOA_MEMO_ROOT"] / memo_relative
    eval_catalog_path = roots["AOA_EVALS_ROOT"] / "generated/eval_catalog.min.json"

    for path in (continuity_path, playbook_path, memo_path, eval_catalog_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    continuity_path.write_text(
        json.dumps(continuity or continuity_payload()), encoding="utf-8"
    )
    playbook_path.write_text(playbook or playbook_text(), encoding="utf-8")
    memo_path.write_text(json.dumps(memo or memo_payload()), encoding="utf-8")
    eval_catalog_path.write_text(
        json.dumps(
            {"catalog_version": eval_catalog_version, "evals": evals or eval_entries()}
        ),
        encoding="utf-8",
    )
    return roots


def set_reference_roots(
    monkeypatch: pytest.MonkeyPatch, roots: dict[str, Path]
) -> None:
    for env_name, root in roots.items():
        monkeypatch.setenv(env_name, str(root))


def test_reference_adapter_core_and_root_facade_preserve_committed_output() -> None:
    facade = load_build_views_module()
    source, continuity, memo = facade.continuity_window_generated_from()

    pure_summary = continuity_window.build_continuity_window_summary(
        source, continuity, memo
    )
    facade_summary = facade.build_continuity_window_summary()
    committed_path = REPO_ROOT / "generated" / "continuity_window_summary.min.json"
    committed_bytes = committed_path.read_bytes()
    committed_summary = json.loads(committed_bytes)
    schema = json.loads(
        (REPO_ROOT / "schemas" / "continuity-window-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert pure_summary == facade_summary == committed_summary
    Draft202012Validator(schema).validate(pure_summary)
    assert facade.stable_json(facade_summary).encode() == committed_bytes
    assert hashlib.sha256(committed_bytes).hexdigest() == EXPECTED_COMMITTED_SHA256


def test_part_example_and_profile_keep_committed_reference_contract() -> None:
    profile = json.loads(
        (
            REPO_ROOT
            / "stats/read-models/active/continuity_window_summary.profile.json"
        ).read_text(encoding="utf-8")
    )
    schema = json.loads(
        (REPO_ROOT / "schemas/continuity-window-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )
    example = json.loads(
        (PART_ROOT / "examples/continuity_window_summary.example.json").read_text(
            encoding="utf-8"
        )
    )
    committed = json.loads(
        (REPO_ROOT / "generated/continuity_window_summary.min.json").read_text(
            encoding="utf-8"
        )
    )
    strength_model = (
        REPO_ROOT / "stats/surface-catalog/SURFACE_STRENGTH_MODEL.md"
    ).read_text(encoding="utf-8")

    assert profile["input_posture"] == (
        "committed_reference_example_catalog_chain"
    )
    assert profile["live_state_capable"] is False
    assert profile["owner_truth_inputs"] == [
        "aoa-agents/mechanics/checkpoint/parts/continuity-lane/examples/"
        "self-agency-continuity-window.example.json",
        "aoa-playbooks/playbooks/continuity/session-growth/"
        "self-agency-continuity-cycle/PLAYBOOK.md",
        "aoa-memo/mechanics/writeback/parts/growth-and-continuity/examples/"
        "provenance_thread.self-agency-continuity.example.json",
        "aoa-evals/generated/eval_catalog.min.json",
    ]
    assert "`committed_reference_example_catalog_chain`" in strength_model
    Draft202012Validator(schema).validate(example)
    assert example == committed


def test_root_facade_preserves_continuity_compatibility_symbols() -> None:
    facade = load_build_views_module()

    assert facade.CONTINUITY_STATUSES is continuity_window.CONTINUITY_STATUSES
    assert facade.CONTINUITY_EVAL_ANCHORS is continuity_window.CONTINUITY_EVAL_ANCHORS
    assert facade.continuity_reanchor_counts is continuity_window.continuity_reanchor_counts
    assert facade.continuity_drift_flags is continuity_window.continuity_drift_flags
    assert not inspect.signature(facade.continuity_window_source_paths).parameters
    assert not inspect.signature(facade.continuity_window_generated_from).parameters
    source, continuity, memo = facade.continuity_window_generated_from()
    assert isinstance(source, dict)
    assert isinstance(continuity, dict)
    assert isinstance(memo, dict)


def test_continuity_input_bundle_is_deeply_immutable_and_detached() -> None:
    source = {
        "receipt_input_paths": ["agents", "playbook", "memo", "evals"],
        "total_receipts": 1,
        "latest_observed_at": "2026-04-12T14:20:00Z",
    }
    continuity = continuity_payload()
    memo = memo_payload()
    bundle = ContinuityWindowInputBundle(source, continuity, memo)

    source["receipt_input_paths"].append("later")
    continuity["continuity_ref"] = "mutated"
    memo["timeline"][0]["action"] = "mutated"

    assert bundle.source["receipt_input_paths"] == (
        "agents",
        "playbook",
        "memo",
        "evals",
    )
    assert bundle.continuity_window["continuity_ref"] == "CONT-test-01"
    assert bundle.memo_thread["timeline"][0]["action"] == (
        "published the bounded continuity window"
    )
    with pytest.raises(TypeError):
        bundle.source["total_receipts"] = 2  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.memo_thread["timeline"][0]["action"] = "mutated"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        bundle.source = {}  # type: ignore[misc]


def test_committed_facade_passes_immutable_bundle_to_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()

    def capture_bundle(source, continuity, memo):
        assert isinstance(source["receipt_input_paths"], tuple)
        assert isinstance(memo["timeline"], tuple)
        with pytest.raises(TypeError):
            source["total_receipts"] = 2
        with pytest.raises(TypeError):
            continuity["continuity_ref"] = "mutated"
        return {"schema_version": "captured-immutable-bundle"}

    monkeypatch.setattr(
        facade,
        "build_continuity_window_summary_from_inputs",
        capture_bundle,
    )

    assert facade.build_continuity_window_summary() == {
        "schema_version": "captured-immutable-bundle"
    }


def test_pure_projection_does_not_mutate_inputs() -> None:
    source = {
        "receipt_input_paths": ["agents", "playbook", "memo", "evals"],
        "total_receipts": 1,
        "latest_observed_at": "2026-04-12T14:20:00Z",
    }
    continuity = continuity_payload()
    memo = memo_payload()
    original = deepcopy((source, continuity, memo))

    continuity_window.build_continuity_window_summary(source, continuity, memo)

    assert (source, continuity, memo) == original


@pytest.mark.parametrize(
    "ref_name",
    (
        "continuity_ref",
        "revision_window_ref",
        "reanchor_ref",
        "anchor_artifact_ref",
    ),
)
def test_reference_adapter_rejects_cross_owner_ref_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ref_name: str,
) -> None:
    facade = load_build_views_module()
    memo = memo_payload()
    memo[ref_name] = f"drifted-{ref_name}"
    roots = write_reference_tree(tmp_path, memo=memo)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(
        facade.ReceiptValidationError,
        match=rf"preserve the {ref_name} from aoa-agents",
    ):
        facade.build_continuity_window_summary()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("agent_id", "", "agent_id must be a non-empty string"),
        ("role", "", "role must be a non-empty string"),
        ("rollback_marker", "", "rollback_marker must be a non-empty string"),
        ("memory_scope", "planet", "memory_scope is outside"),
        ("approval_mode", "automatic", "approval_mode is outside"),
        ("max_iterations", 0, "positive max_iterations"),
    ),
)
def test_reference_adapter_rejects_owner_window_contract_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: Any,
    message: str,
) -> None:
    facade = load_build_views_module()
    continuity = continuity_payload()
    continuity[field] = value
    roots = write_reference_tree(tmp_path, continuity=continuity)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(facade.ReceiptValidationError, match=message):
        facade.build_continuity_window_summary()


@pytest.mark.parametrize(
    ("mutate", "message"),
    (
        (lambda payload: payload.pop("role"), "missing required fields: role"),
        (
            lambda payload: payload.update({"unexpected": True}),
            "unsupported fields: unexpected",
        ),
        (
            lambda payload: payload.update({"notes": []}),
            "notes must be a string or null",
        ),
    ),
)
def test_reference_adapter_rejects_owner_window_shape_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutate,
    message: str,
) -> None:
    facade = load_build_views_module()
    continuity = continuity_payload()
    mutate(continuity)
    roots = write_reference_tree(tmp_path, continuity=continuity)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(facade.ReceiptValidationError, match=message):
        facade.build_continuity_window_summary()


@pytest.mark.parametrize("invalid_at", ("not-a-date", ""))
def test_reference_adapter_rejects_every_invalid_timeline_timestamp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    invalid_at: str,
) -> None:
    facade = load_build_views_module()
    memo = memo_payload()
    memo["timeline"][1]["at"] = invalid_at
    roots = write_reference_tree(tmp_path, memo=memo)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(
        facade.ReceiptValidationError,
        match=r"timeline\[1\]\.at must be a date-time",
    ):
        facade.build_continuity_window_summary()


def test_reference_adapter_rejects_unordered_timeline_timestamps(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()
    memo = memo_payload()
    memo["timeline"] = list(reversed(memo["timeline"]))
    roots = write_reference_tree(tmp_path, memo=memo)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(
        facade.ReceiptValidationError,
        match="timeline timestamps must stay ordered",
    ):
        facade.build_continuity_window_summary()


def test_reanchored_status_does_not_manufacture_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()
    memo = memo_payload()
    memo["timeline"][-1]["note"] = "completed reanchor appears only in prose"
    roots = write_reference_tree(
        tmp_path,
        continuity=continuity_payload(status="reanchored"),
        memo=memo,
    )
    set_reference_roots(monkeypatch, roots)

    summary = facade.build_continuity_window_summary()

    assert summary["current_status"] == "reanchored"
    assert summary["successful_reanchors"] == 0
    assert summary["failed_reanchors"] == 0


def test_reanchor_counts_require_explicit_ordered_timeline_actions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()
    memo = memo_payload(
        timeline=[
            {
                "at": "2026-04-12T13:50:00Z",
                "action": "published the bounded continuity window",
            },
            {
                "at": "2026-04-12T14:00:00Z",
                "action": "failed reanchor after anchor verification",
            },
            {
                "at": "2026-04-12T14:20:00Z",
                "action": "completed reanchor to the named artifact",
            },
        ]
    )
    roots = write_reference_tree(
        tmp_path,
        continuity=continuity_payload(status="reanchored"),
        memo=memo,
    )
    set_reference_roots(monkeypatch, roots)

    summary = facade.build_continuity_window_summary()

    assert summary["successful_reanchors"] == 1
    assert summary["failed_reanchors"] == 1
    assert summary["drift_flags"] == ["failed_reanchor_present"]
    assert summary["generated_from"]["latest_observed_at"] == (
        "2026-04-12T14:20:00Z"
    )


@pytest.mark.parametrize(
    "action",
    (
        "reanchor was not completed because the anchor was missing",
        "never completed reanchor",
        "never returned through reanchor",
        "failed to complete reanchor",
        "reanchor completion failed",
    ),
)
def test_negated_reanchor_completion_is_failure_not_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    action: str,
) -> None:
    facade = load_build_views_module()
    memo = memo_payload(
        timeline=[
            {
                "at": "2026-04-12T14:20:00Z",
                "action": action,
            }
        ]
    )
    roots = write_reference_tree(
        tmp_path,
        continuity=continuity_payload(status="reanchored"),
        memo=memo,
    )
    set_reference_roots(monkeypatch, roots)

    summary = facade.build_continuity_window_summary()

    assert summary["successful_reanchors"] == 0
    assert summary["failed_reanchors"] == 1
    assert summary["drift_flags"] == ["failed_reanchor_present"]


@pytest.mark.parametrize(
    ("playbook", "message"),
    (
        (playbook_text(playbook_id="AOA-P-wrong"), "must keep id AOA-P-0029"),
        (
            playbook_text(expected_artifacts=["continuity_window"]),
            "missing expected artifacts",
        ),
        (
            playbook_text(
                eval_anchors=list(continuity_window.CONTINUITY_EVAL_ANCHORS[:-1])
            ),
            "eval_anchors must match",
        ),
        (
            playbook_text(fallback_mode="continue"),
            "must keep review_required fallback",
        ),
    ),
)
def test_reference_adapter_rejects_playbook_contract_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    playbook: str,
    message: str,
) -> None:
    facade = load_build_views_module()
    roots = write_reference_tree(tmp_path, playbook=playbook)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(facade.ReceiptValidationError, match=message):
        facade.build_continuity_window_summary()


@pytest.mark.parametrize(
    ("mutate", "message"),
    (
        (
            lambda entries: entries.pop(),
            "missing continuity anchors",
        ),
        (
            lambda entries: entries.append(dict(entries[0])),
            "must not duplicate anchor",
        ),
        (
            lambda entries: entries[0].update({"eval_path": "evals/wrong/EVAL.md"}),
            "canonical eval_path",
        ),
        (
            lambda entries: entries[0].update({"claim_type": "comparative"}),
            "bounded claim_type",
        ),
        (
            lambda entries: entries[0].update({"review_required": False}),
            "keep review_required",
        ),
        (
            lambda entries: entries[0].update({"status": "bogus"}),
            "keep draft reference status",
        ),
    ),
)
def test_reference_adapter_rejects_eval_anchor_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutate,
    message: str,
) -> None:
    facade = load_build_views_module()
    entries = eval_entries()
    mutate(entries)
    roots = write_reference_tree(tmp_path, evals=entries)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(facade.ReceiptValidationError, match=message):
        facade.build_continuity_window_summary()


def test_reference_adapter_rejects_eval_catalog_version_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()
    roots = write_reference_tree(tmp_path, eval_catalog_version=999)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(
        facade.ReceiptValidationError, match="eval catalog must keep version 1"
    ):
        facade.build_continuity_window_summary()


def test_reference_adapter_rejects_garbage_memo_source_refs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()
    memo = memo_payload()
    memo["source_refs"] = [
        "repo:aoa-agents/garbage",
        "repo:aoa-playbooks/garbage",
        "repo:aoa-evals/garbage",
    ]
    roots = write_reference_tree(tmp_path, memo=memo)
    set_reference_roots(monkeypatch, roots)

    with pytest.raises(
        facade.ReceiptValidationError,
        match="source_refs must cite aoa-agents/",
    ):
        facade.build_continuity_window_summary()


def test_reference_adapter_reports_the_resolved_legacy_memo_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()
    roots = write_reference_tree(tmp_path, legacy_memo_path=True)
    set_reference_roots(monkeypatch, roots)

    summary = facade.build_continuity_window_summary()

    assert summary["generated_from"]["receipt_input_paths"][2] == (
        "aoa-memo/mechanics/writeback/examples/"
        "provenance_thread.self-agency-continuity.example.json"
    )


def test_optional_output_allowlist_skips_reference_adapter_before_invocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()
    receipts = facade.load_receipts([RECEIPT_FIXTURE])

    def fail_if_called(**_roots):
        raise AssertionError("continuity reference adapter must not run when excluded")

    monkeypatch.setattr(
        facade,
        "load_continuity_window_reference_bundle",
        fail_if_called,
    )
    outputs = facade.build_all_views(
        receipts,
        ["stats/intake-contract/examples/session_harvest_family.receipts.example.json"],
        optional_output_names=frozenset(),
    )

    assert "continuity_window_summary.min.json" not in outputs
    assert all(
        entry["name"] != "continuity_window_summary"
        for entry in outputs["summary_surface_catalog.min.json"]["surfaces"]
    )
