from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"
RECEIPT_FIXTURE = (
    REPO_ROOT
    / "stats"
    / "intake-contract"
    / "examples"
    / "session_harvest_family.receipts.example.json"
)
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import component_refresh  # noqa: E402
from aoa_stats_builder.component_refresh_sources import (  # noqa: E402
    ComponentRefreshInputBundle,
)


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def component_hint(
    *,
    hint_ref: str = "hint:root",
    component_ref: str = "component:codex-plane:shared-root",
    owner_repo: str = "8Dionysus",
    observed_at: str = "2026-04-12T16:20:00Z",
    signals: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    route_class: str = "regenerate",
) -> dict[str, Any]:
    return {
        "hint_ref": hint_ref,
        "component_ref": component_ref,
        "owner_repo": owner_repo,
        "observed_at": observed_at,
        "observed_by": "workspace_root",
        "severity": "medium",
        "signals": signals or ["doctor_fail_after_render"],
        "repeat_count": 1,
        "evidence_refs": (
            ["artifact:root"] if evidence_refs is None else evidence_refs
        ),
        "recommended_route_class": route_class,
        "review_required": True,
    }


def component_decision(
    *,
    component_ref: str = "component:codex-plane:shared-root",
    owner_repo: str = "8Dionysus",
    route_class: str = "regenerate",
    decision_status: str = "chosen",
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "component_ref": component_ref,
        "owner_repo": owner_repo,
        "route_class": route_class,
        "decision_status": decision_status,
        "selected_refresh_path": ["python refresh.py"],
        "reason": "bounded reviewed route",
        "evidence_refs": ["hint:root"] if evidence_refs is None else evidence_refs,
        "rollback_anchor": "docs/ROLLBACK.md",
        "stats_should_refresh": True,
        "memo_writeback_candidate": False,
    }


def write_sdk_example_bundle(
    tmp_path: Path,
    *,
    hints: list[dict[str, Any]] | None = None,
    decisions: list[dict[str, Any]] | None = None,
    reviewed: bool = True,
) -> Path:
    sdk_root = tmp_path / ".deps" / "aoa-sdk"
    examples_root = (
        sdk_root
        / "mechanics"
        / "checkpoint"
        / "parts"
        / "reviewed-closeout-context-carry"
        / "examples"
    )
    examples_root.mkdir(parents=True)
    (examples_root / "component_drift_hints.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_drift_hint_set_v1",
                "session_ref": "session:component-refresh-test",
                "repo_root": "/srv/AbyssOS",
                "hints": hints or [component_hint()],
            }
        ),
        encoding="utf-8",
    )
    (
        examples_root / "component_refresh_followthrough_decision.example.json"
    ).write_text(
        json.dumps(
            {
                "schema_version": (
                    "aoa_component_refresh_followthrough_decision_set_v1"
                ),
                "decision_ref": "decision:test",
                "reviewed": reviewed,
                "session_ref": "session:component-refresh-test",
                "decisions": decisions or [component_decision()],
            }
        ),
        encoding="utf-8",
    )
    return sdk_root


def test_reference_adapter_core_and_root_facade_preserve_committed_output() -> None:
    facade = load_build_views_module()
    source, hints, decisions = facade.component_refresh_generated_from()

    pure_summary = component_refresh.build_component_refresh_summary(
        source, hints, decisions
    )
    facade_summary = facade.build_component_refresh_summary()
    committed_summary = json.loads(
        (REPO_ROOT / "generated" / "component_refresh_summary.min.json").read_text(
            encoding="utf-8"
        )
    )
    schema = json.loads(
        (REPO_ROOT / "schemas" / "component-refresh-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert pure_summary == facade_summary == committed_summary
    Draft202012Validator(schema).validate(pure_summary)
    assert facade.stable_json(facade_summary) == (
        REPO_ROOT / "generated" / "component_refresh_summary.min.json"
    ).read_text(encoding="utf-8")


def test_component_refresh_input_bundle_is_deeply_immutable_and_detached() -> None:
    source = {
        "receipt_input_paths": ["hints", "decisions"],
        "total_receipts": 2,
        "latest_observed_at": "2026-04-12T16:20:00Z",
    }
    hints = [component_hint(signals=["doctor_fail_after_render"])]
    decisions = [component_decision()]
    bundle = ComponentRefreshInputBundle(source, hints, decisions)

    source["receipt_input_paths"].append("later")
    hints[0]["signals"].append("later")
    decisions[0]["owner_repo"] = "mutated"

    assert bundle.source["receipt_input_paths"] == ("hints", "decisions")
    assert bundle.hints[0]["signals"] == ("doctor_fail_after_render",)
    assert bundle.decisions[0]["owner_repo"] == "8Dionysus"
    with pytest.raises(TypeError):
        bundle.source["total_receipts"] = 3  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.hints[0]["owner_repo"] = "mutated"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        bundle.source = {}  # type: ignore[misc]


def test_committed_facade_passes_immutable_bundle_to_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()

    def capture_bundle(source, hints, decisions):
        assert isinstance(hints, tuple)
        assert isinstance(decisions, tuple)
        with pytest.raises(TypeError):
            source["total_receipts"] = 3
        with pytest.raises(TypeError):
            hints[0]["owner_repo"] = "mutated"
        return {"schema_version": "captured-immutable-bundle"}

    monkeypatch.setattr(
        facade,
        "build_component_refresh_summary_from_inputs",
        capture_bundle,
    )

    assert facade.build_component_refresh_summary() == {
        "schema_version": "captured-immutable-bundle"
    }


def test_pure_projection_does_not_mutate_inputs() -> None:
    source = {
        "receipt_input_paths": ["hints", "decisions"],
        "total_receipts": 2,
        "latest_observed_at": "2026-04-12T16:20:00Z",
    }
    hints = [component_hint()]
    decisions = [component_decision()]
    original = deepcopy((source, hints, decisions))

    component_refresh.build_component_refresh_summary(source, hints, decisions)

    assert (source, hints, decisions) == original


def test_component_refresh_summary_stays_derived_and_non_sovereign(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    facade = load_build_views_module()
    hints = [
        component_hint(
            signals=["doctor_fail_after_render", "same_hand_patch_repeated"]
        ),
        component_hint(
            hint_ref="hint:stats",
            component_ref="component:stats-derived-summaries:growth-refinery",
            owner_repo="aoa-stats",
            observed_at="2026-04-12T16:31:00Z",
            signals=["latest_observed_at_stale", "summary_family_out_of_sync"],
            route_class="rebuild",
        ),
    ]
    decisions = [
        component_decision(),
        component_decision(
            component_ref="component:stats-derived-summaries:growth-refinery",
            owner_repo="aoa-stats",
            route_class="rebuild",
            evidence_refs=["hint:stats"],
        ),
    ]
    sdk_root = write_sdk_example_bundle(
        tmp_path, hints=hints, decisions=decisions
    )
    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    summary = facade.build_component_refresh_summary()

    assert summary["owner_repo_counts"] == {"8Dionysus": 1, "aoa-stats": 1}
    assert summary["status_counts"] == {
        "refresh_recommended": 1,
        "refresh_active": 1,
        "current": 0,
        "deferred": 0,
        "recovered": 0,
    }
    assert summary["drift_class_counts"] == {
        "doctor_drift": 1,
        "family_drift": 1,
        "manual_repeat": 1,
        "root_drift": 1,
        "staleness_window": 1,
    }


def test_reference_adapter_rejects_empty_hint_evidence_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    facade = load_build_views_module()
    sdk_root = write_sdk_example_bundle(
        tmp_path, hints=[component_hint(evidence_refs=[])]
    )
    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    with pytest.raises(
        facade.ReceiptValidationError, match="must expose at least one evidence_ref"
    ):
        facade.build_component_refresh_summary()


def test_reference_adapter_rejects_duplicate_decisions_for_component(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    facade = load_build_views_module()
    sdk_root = write_sdk_example_bundle(
        tmp_path,
        decisions=[
            component_decision(),
            component_decision(route_class="repair", decision_status="deferred"),
        ],
    )
    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    with pytest.raises(
        facade.ReceiptValidationError, match="must not duplicate component_ref"
    ):
        facade.build_component_refresh_summary()


def test_reference_adapter_rejects_cross_component_hint_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    facade = load_build_views_module()
    sdk_root = write_sdk_example_bundle(
        tmp_path,
        decisions=[
            component_decision(
                component_ref="component:other",
                owner_repo="repo-other",
                evidence_refs=["hint:root"],
            )
        ],
    )
    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    with pytest.raises(
        facade.ReceiptValidationError,
        match="component_ref must match cited hint",
    ):
        facade.build_component_refresh_summary()


def test_reference_adapter_rejects_cross_owner_hint_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    facade = load_build_views_module()
    sdk_root = write_sdk_example_bundle(
        tmp_path,
        decisions=[
            component_decision(
                owner_repo="repo-other",
                evidence_refs=["hint:root"],
            )
        ],
    )
    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    with pytest.raises(
        facade.ReceiptValidationError,
        match="owner_repo must match cited hint",
    ):
        facade.build_component_refresh_summary()


def test_reference_adapter_rejects_external_evidence_when_matching_hint_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    facade = load_build_views_module()
    sdk_root = write_sdk_example_bundle(
        tmp_path,
        decisions=[component_decision(evidence_refs=["repo:owner/review.md"])],
    )
    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    with pytest.raises(
        facade.ReceiptValidationError,
        match="must cite matching hint_ref 'hint:root'",
    ):
        facade.build_component_refresh_summary()


def test_decision_only_component_keeps_null_freshness_and_external_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    facade = load_build_views_module()
    hints = [
        component_hint(
            hint_ref="hint:other",
            component_ref="component:other",
            owner_repo="repo-other",
            observed_at="2026-04-12T10:00:00Z",
        )
    ]
    decisions = [
        component_decision(
            component_ref="component:no-hint",
            owner_repo="repo-no-hint",
            route_class="repair",
            evidence_refs=["repo:owner/review.md"],
        )
    ]
    sdk_root = write_sdk_example_bundle(
        tmp_path, hints=hints, decisions=decisions
    )
    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    summary = facade.build_component_refresh_summary()
    decision_only = next(
        component
        for component in summary["components"]
        if component["component_ref"] == "component:no-hint"
    )

    assert summary["generated_from"]["latest_observed_at"] == "2026-04-12T10:00:00Z"
    assert decision_only == {
        "component_ref": "component:no-hint",
        "owner_repo": "repo-no-hint",
        "latest_decision_status": "chosen",
        "current_status": "refresh_active",
        "latest_route_class": "repair",
        "latest_observed_at": None,
    }


def test_pure_projection_selects_latest_hint_per_component() -> None:
    source = {
        "receipt_input_paths": ["hints", "decisions"],
        "total_receipts": 2,
        "latest_observed_at": "2026-04-12T16:20:00Z",
    }
    hints = [
        component_hint(
            hint_ref="hint:old",
            component_ref="component:test",
            owner_repo="aoa-stats",
            observed_at="2026-04-12T16:00:00Z",
            route_class="observe",
        ),
        component_hint(
            hint_ref="hint:new",
            component_ref="component:test",
            owner_repo="aoa-stats",
            observed_at="2026-04-12T16:20:00Z",
            route_class="repair",
        ),
    ]

    summary = component_refresh.build_component_refresh_summary(source, hints, [])

    assert summary["components"][0]["latest_route_class"] == "repair"
    assert summary["components"][0]["latest_observed_at"] == "2026-04-12T16:20:00Z"


def test_optional_output_allowlist_skips_reference_adapter_before_invocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade = load_build_views_module()
    receipts = facade.load_receipts([RECEIPT_FIXTURE])

    def fail_if_called(_sdk_root: Path):
        raise AssertionError("reference adapter must not run for an excluded output")

    monkeypatch.setattr(facade, "load_reviewed_sdk_example_bundle", fail_if_called)
    outputs = facade.build_all_views(
        receipts,
        ["stats/intake-contract/examples/session_harvest_family.receipts.example.json"],
        optional_output_names=frozenset(),
    )

    assert "component_refresh_summary.min.json" not in outputs
    assert all(
        entry["name"] != "component_refresh_summary"
        for entry in outputs["summary_surface_catalog.min.json"]["surfaces"]
    )
