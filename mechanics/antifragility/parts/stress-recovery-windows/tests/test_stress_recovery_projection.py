from __future__ import annotations

import ast
import inspect
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
RECEIPT_FIXTURE_REF = (
    "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
)
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import stress_recovery  # noqa: E402
from aoa_stats_builder.receipt_abi import generated_from, load_receipts  # noqa: E402
from aoa_stats_builder.stress_recovery_sources import (  # noqa: E402
    COMMITTED_REFERENCE_CURRENT_REPORT_PATH,
    COMMITTED_REFERENCE_LEGACY_REPORT_REF,
    load_stress_recovery_committed_reference_report,
    load_stress_recovery_report,
    resolve_aoa_evals_report_path,
)


def resolve_evals_root() -> Path:
    candidates = (
        os.environ.get("AOA_EVALS_ROOT"),
        str(REPO_ROOT / ".deps" / "aoa-evals"),
        str(REPO_ROOT.parent / "aoa-evals"),
        "/srv/AbyssOS/aoa-evals",
    )
    for candidate in candidates:
        if candidate and (Path(candidate) / COMMITTED_REFERENCE_CURRENT_REPORT_PATH).is_file():
            return Path(candidate).expanduser().resolve()
    raise RuntimeError("could not resolve the aoa-evals committed reference root")


def load_checked_receipts() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fixture_path = REPO_ROOT / RECEIPT_FIXTURE_REF
    receipts = load_receipts([fixture_path])
    return receipts, generated_from(receipts, [RECEIPT_FIXTURE_REF])


def stress_receipt(report_ref: str) -> dict[str, Any]:
    return {
        "event_kind": "eval_result_receipt",
        "event_id": "evt-stress-window-focused-0001",
        "observed_at": "2026-04-07T18:01:00Z",
        "run_ref": "run-stress-window-focused-001",
        "session_ref": "session:stress-window-focused",
        "actor_ref": "aoa-evals:reviewer",
        "object_ref": {
            "repo": "aoa-evals",
            "kind": "eval_bundle",
            "id": "aoa-stress-recovery-window",
            "version": "draft",
        },
        "evidence_refs": [],
        "payload": {
            "eval_name": "aoa-stress-recovery-window",
            "report_ref": report_ref,
        },
    }


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def test_core_and_explicit_reference_adapter_preserve_committed_output() -> None:
    receipts, source = load_checked_receipts()
    original_receipts = deepcopy(receipts)
    original_source = deepcopy(source)
    report_ref = stress_recovery.latest_stress_recovery_report_ref(receipts)
    report = load_stress_recovery_committed_reference_report(
        resolve_evals_root(), report_ref
    )
    original_report = deepcopy(report)

    projected = stress_recovery.build_stress_recovery_window_summary(
        receipts,
        source,
        report=report,
    )

    generated_path = REPO_ROOT / "generated/stress_recovery_window_summary.min.json"
    schema = json.loads(
        (REPO_ROOT / "schemas/stress-recovery-window-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert stable_json(projected) == generated_path.read_text(encoding="utf-8")
    Draft202012Validator(schema).validate(projected)
    assert receipts == original_receipts
    assert source == original_source
    assert report == original_report

    core_tree = ast.parse(inspect.getsource(stress_recovery))
    imported_modules = {
        alias.name
        for node in ast.walk(core_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(core_tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert "pathlib" not in imported_modules
    assert "os" not in imported_modules
    assert not any(
        isinstance(node, ast.Attribute)
        and node.attr in {"read_bytes", "read_text", "write_bytes", "write_text"}
        for node in ast.walk(core_tree)
    )


def test_unsuppressed_projection_connects_counts_to_metrics() -> None:
    report_ref = "repo:aoa-evals/reports/active-window.json"
    receipts = [stress_receipt(report_ref)]
    source = generated_from(receipts, ["memory"])
    report = {
        "window": {
            "label": "active-window",
            "start_utc": "2026-04-01T00:00:00Z",
            "end_utc": "2026-04-07T00:00:00Z",
        },
        "scope": {
            "repo_roots": ["aoa-evals", "aoa-routing"],
            "stressor_family": "hybrid-query-kag-unhealthy",
            "owner_surface": "hybrid-query",
            "surface_family": "kag-regrounding",
        },
        "inputs": {
            "source_receipt_refs": ["r1", "r2"],
            "handoff_refs": ["h1"],
            "playbook_lane_refs": ["p1"],
            "reentry_gate_refs": ["g1"],
            "projection_health_refs": ["ph1"],
            "regrounding_ticket_refs": ["rt1"],
            "route_hint_refs": ["route1"],
            "memo_context_refs": ["memo1"],
        },
        "axes": {
            "handoff_fidelity": {"score": 0.9},
            "route_discipline": {"score": 0.88},
            "reentry_quality": {"score": 0.72},
            "regrounding_effectiveness": {"score": 0.69},
            "evidence_continuity": {"score": 0.91},
            "false_promotion_prevention": {"score": 0.93},
            "operator_burden": {"score": 0.64},
            "trust_calibration": {"score": 0.89},
        },
        "overall_posture": "mixed",
    }
    original_report = deepcopy(report)

    projected = stress_recovery.build_stress_recovery_window_summary(
        receipts,
        source,
        report=report,
    )

    assert projected["suppression"] == {"status": "none", "reason": None}
    assert projected["counts"] == {
        "receipt_count": 2,
        "handoff_count": 1,
        "playbook_lane_count": 1,
        "reentry_gate_count": 1,
        "projection_health_count": 1,
        "regrounding_ticket_count": 1,
        "eval_count": 1,
    }
    assert projected["summary"]["containment"] == 0.9
    assert projected["summary"]["adaptation_followthrough"] == 0.68
    assert projected["inputs"]["eval_report_refs"] == [report_ref]
    assert "false-promotion-guard-held" in projected["trend_flags"]
    assert report == original_report


def test_exact_adapter_resolves_only_safe_aoa_evals_repo_refs(tmp_path: Path) -> None:
    evals_root = tmp_path / "aoa-evals"
    relative_path = Path("reports/active-window.json")
    report_path = evals_root / relative_path
    report_path.parent.mkdir(parents=True)
    report_path.write_text('{"report_id": "active-window"}\n', encoding="utf-8")
    report_ref = f"repo:aoa-evals/{relative_path.as_posix()}"

    assert resolve_aoa_evals_report_path(evals_root, report_ref) == report_path.resolve()
    assert load_stress_recovery_report(evals_root, report_ref) == {
        "report_id": "active-window"
    }

    for invalid_ref in (
        "repo:aoa-memo/reports/active-window.json",
        "repo:aoa-evals/../outside.json",
        "repo:aoa-evals//absolute.json",
        "/tmp/active-window.json",
        None,
    ):
        assert resolve_aoa_evals_report_path(evals_root, invalid_ref) is None
        assert load_stress_recovery_report(evals_root, invalid_ref) is None


def test_committed_reference_legacy_alias_is_explicit(tmp_path: Path) -> None:
    evals_root = tmp_path / "aoa-evals"
    current_path = evals_root / COMMITTED_REFERENCE_CURRENT_REPORT_PATH
    current_path.parent.mkdir(parents=True)
    current_path.write_text('{"report_id": "current-example"}\n', encoding="utf-8")

    assert (
        load_stress_recovery_report(
            evals_root,
            COMMITTED_REFERENCE_LEGACY_REPORT_REF,
        )
        is None
    )
    assert load_stress_recovery_committed_reference_report(
        evals_root,
        COMMITTED_REFERENCE_LEGACY_REPORT_REF,
    ) == {"report_id": "current-example"}

    unrelated_legacy_ref = (
        "repo:aoa-evals/bundles/another-window/reports/example-report.json"
    )
    assert (
        load_stress_recovery_committed_reference_report(
            evals_root,
            unrelated_legacy_ref,
        )
        is None
    )


@pytest.mark.parametrize("malformed", (False, True))
def test_missing_or_malformed_report_suppresses_projection(
    tmp_path: Path,
    malformed: bool,
) -> None:
    evals_root = tmp_path / "aoa-evals"
    report_ref = "repo:aoa-evals/reports/unavailable.json"
    if malformed:
        report_path = evals_root / "reports/unavailable.json"
        report_path.parent.mkdir(parents=True)
        report_path.write_text("{not-json}\n", encoding="utf-8")
    receipts = [stress_receipt(report_ref)]
    source = generated_from(receipts, ["memory"])
    report = load_stress_recovery_report(evals_root, report_ref)

    projected = stress_recovery.build_stress_recovery_window_summary(
        receipts,
        source,
        report=report,
    )

    assert report is None
    assert projected["suppression"] == {
        "status": "insufficient_evidence",
        "reason": (
            "report_ref for aoa-stress-recovery-window could not be resolved "
            "into a readable aoa-evals JSON report"
        ),
    }
    assert projected["summary"]["containment"] is None
