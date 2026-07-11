from __future__ import annotations

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
SRC_ROOT = REPO_ROOT / "src"
BUILD_VIEWS_PATH = REPO_ROOT / "scripts" / "build_views.py"
RECEIPT_FIXTURE = (
    REPO_ROOT
    / "stats/intake-contract/examples/"
    "session_harvest_family.receipts.example.json"
)
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import codex_plane_deployment  # noqa: E402
from aoa_stats_builder.codex_plane_deployment_sources import (  # noqa: E402
    CodexPlaneDeploymentInputBundle,
    codex_plane_live_paths,
    codex_plane_reference_paths,
    load_codex_plane_live_bundle,
    load_codex_plane_reference_bundle,
)


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", BUILD_VIEWS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def trust_payload() -> dict[str, Any]:
    stable_names = list(codex_plane_deployment.CODEX_PLANE_V1_STABLE_MCP_NAMES)
    return {
        "schema_version": "8dionysus_codex_plane_trust_state_v1",
        "trust_state_id": "trust-test-01",
        "workspace_root": "/srv/test-workspace",
        "detected_project_root": "/srv/test-workspace",
        "project_root_markers_expected": ["AOA_WORKSPACE_ROOT", ".git"],
        "project_root_marker_match": ["AOA_WORKSPACE_ROOT"],
        "project_config_active": True,
        "active_config_layers": ["/srv/test-workspace/.codex/config.toml"],
        "hooks_enabled": True,
        "hook_layers_detected": ["/srv/test-workspace/.codex/hooks.json"],
        "mcp_server_names_expected": list(stable_names),
        "mcp_server_names_detected": list(stable_names),
        "stable_names_ok": True,
        "trust_posture": "trusted_ready",
        "warnings": [],
        "captured_at": "2026-04-11T21:04:00Z",
    }


def regeneration_payload() -> dict[str, Any]:
    return {
        "schema_version": "8dionysus_codex_plane_regeneration_report_v1",
        "regeneration_report_id": "regen-test-01",
        "source_profile_ref": "8Dionysus:config/codex_plane/test.json",
        "target_workspace_root": "/srv/test-workspace",
        "render_posture": "execute",
        "rendered_files": [
            {
                "relative_path": ".codex/config.toml",
                "source_path": "8Dionysus:config/codex_plane/runtime_manifest.v1.json",
                "mode": "rewrite",
                "changed": True,
                "sha256": "a" * 64,
            },
            {
                "relative_path": ".codex/hooks.json",
                "source_path": "8Dionysus:config/codex_plane/runtime_manifest.v1.json",
                "mode": "rewrite",
                "changed": True,
                "sha256": "b" * 64,
            },
        ],
        "stable_names": {
            name: True
            for name in codex_plane_deployment.CODEX_PLANE_V1_STABLE_MCP_NAMES
        },
        "warnings": [],
        "generated_at": "2026-04-11T21:05:00Z",
    }


def receipt_payload() -> dict[str, Any]:
    return {
        "schema_version": "8dionysus_codex_plane_rollout_receipt_v1",
        "rollout_receipt_id": "receipt-test-01",
        "trust_state_id": "trust-test-01",
        "regeneration_report_id": "regen-test-01",
        "apply_mode": "execute",
        "deployment_state": "verified",
        "doctor_result": "pass",
        "rollback_plan_ref": "docs/CODEX_PLANE_ROLLOUT.md#rollback-posture",
        "stats_refresh_required": True,
        "verified_at": "2026-04-11T21:07:00Z",
    }


def source_payload(*, refs: list[str] | None = None) -> dict[str, Any]:
    return {
        "receipt_input_paths": refs
        or [
            "8Dionysus/examples/codex_plane_trust_state.example.json",
            "8Dionysus/examples/codex_plane_regeneration_report.example.json",
            "8Dionysus/examples/codex_plane_rollout_receipt.example.json",
        ],
        "total_receipts": 1,
        "latest_observed_at": "2026-04-11T21:07:00Z",
    }


def write_chain(
    root: Path,
    *,
    mode: str,
    trust: dict[str, Any] | None = None,
    regeneration: dict[str, Any] | None = None,
    receipt: dict[str, Any] | None = None,
) -> tuple[Path, Path, Path]:
    paths = (
        codex_plane_reference_paths(root)
        if mode == "reference"
        else codex_plane_live_paths(root)
    )
    trust_data = deepcopy(trust) if trust is not None else trust_payload()
    regeneration_data = (
        deepcopy(regeneration)
        if regeneration is not None
        else regeneration_payload()
    )
    receipt_data = deepcopy(receipt) if receipt is not None else receipt_payload()
    if mode == "live":
        resolved_root = str(root.resolve())
        if trust is None:
            trust_data["workspace_root"] = resolved_root
            trust_data["detected_project_root"] = resolved_root
            trust_data["active_config_layers"] = [
                f"{resolved_root}/.codex/config.toml"
            ]
            trust_data["hook_layers_detected"] = [
                f"{resolved_root}/.codex/hooks.json"
            ]
        if regeneration is None:
            regeneration_data["target_workspace_root"] = resolved_root
    for path, payload in zip(
        paths,
        (trust_data, regeneration_data, receipt_data),
        strict=True,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    return paths


def test_committed_reference_core_facade_example_and_schema_are_aligned() -> None:
    facade = load_build_views_module()
    source, trust, regeneration, receipt = facade.codex_plane_generated_from()
    pure = codex_plane_deployment.build_codex_plane_deployment_summary(
        source, trust, regeneration, receipt
    )
    facade_summary = facade.build_codex_plane_deployment_summary()
    committed = json.loads(
        (REPO_ROOT / "generated/codex_plane_deployment_summary.min.json").read_text(
            encoding="utf-8"
        )
    )
    example = json.loads(
        (REPO_ROOT / "examples/codex_plane_deployment_summary.example.json").read_text(
            encoding="utf-8"
        )
    )
    schema = json.loads(
        (REPO_ROOT / "schemas/codex-plane-deployment-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert pure == facade_summary == committed == example
    Draft202012Validator(schema).validate(committed)
    assert committed["generated_from"]["receipt_input_paths"] == [
        "8Dionysus/examples/codex_plane_trust_state.example.json",
        "8Dionysus/examples/codex_plane_regeneration_report.example.json",
        "8Dionysus/examples/codex_plane_rollout_receipt.example.json",
    ]
    assert committed["stable_mcp_name_set"] == sorted(
        codex_plane_deployment.CODEX_PLANE_V1_STABLE_MCP_NAMES
    )


def test_authored_profile_names_reference_and_stronger_live_surfaces() -> None:
    profile = json.loads(
        (
            REPO_ROOT
            / "stats/read-models/active/"
            "codex_plane_deployment_summary.profile.json"
        ).read_text(encoding="utf-8")
    )

    assert profile["input_posture"] == "committed_owner_example_chain"
    assert profile["live_state_capable"] is False
    assert profile["owner_truth_inputs"] == [
        "8Dionysus/examples/codex_plane_trust_state.example.json",
        "8Dionysus/examples/codex_plane_regeneration_report.example.json",
        "8Dionysus/examples/codex_plane_rollout_receipt.example.json",
        "<workspace-root>/.codex/generated/rollout/"
        "codex_plane_trust_state.current.json",
        "<workspace-root>/.codex/generated/rollout/"
        "codex_plane_regeneration_report.latest.json",
        "<workspace-root>/.codex/generated/rollout/"
        "codex_plane_rollout_receipt.latest.json",
    ]


def test_root_facade_preserves_legacy_codex_plane_symbols_and_tuple() -> None:
    facade = load_build_views_module()

    assert facade.TRUST_POSTURES is codex_plane_deployment.TRUST_POSTURES
    assert not inspect.signature(facade.codex_plane_example_paths).parameters
    assert not inspect.signature(facade.codex_plane_generated_from).parameters
    source, trust, regeneration, receipt = facade.codex_plane_generated_from()
    source["receipt_input_paths"].append("mutable-compatibility")
    trust["trust_state_id"] = "mutable-compatibility"

    assert regeneration["schema_version"].endswith("regeneration_report_v1")
    assert receipt["schema_version"].endswith("rollout_receipt_v1")


def test_input_bundle_is_deeply_immutable_and_detached() -> None:
    source = source_payload()
    trust = trust_payload()
    regeneration = regeneration_payload()
    receipt = receipt_payload()
    bundle = CodexPlaneDeploymentInputBundle(source, trust, regeneration, receipt)

    source["receipt_input_paths"].append("later")
    trust["warnings"].append("later")
    regeneration["rendered_files"][0]["changed"] = False

    assert len(bundle.source["receipt_input_paths"]) == 3
    assert bundle.trust["warnings"] == ()
    assert bundle.regeneration["rendered_files"][0]["changed"] is True
    with pytest.raises(TypeError):
        bundle.trust["trust_state_id"] = "mutated"  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.regeneration["rendered_files"][0]["changed"] = False  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        bundle.source = {}  # type: ignore[misc]


def test_pure_projection_does_not_mutate_inputs() -> None:
    inputs = (
        source_payload(),
        trust_payload(),
        regeneration_payload(),
        receipt_payload(),
    )
    original = deepcopy(inputs)

    codex_plane_deployment.build_codex_plane_deployment_summary(*inputs)

    assert inputs == original


def test_reference_adapter_uses_only_the_three_owner_examples(tmp_path: Path) -> None:
    owner_root = tmp_path / "8Dionysus"
    write_chain(owner_root, mode="reference")

    bundle = load_codex_plane_reference_bundle(owner_root)

    assert bundle.source["receipt_input_paths"] == (
        "8Dionysus/examples/codex_plane_trust_state.example.json",
        "8Dionysus/examples/codex_plane_regeneration_report.example.json",
        "8Dionysus/examples/codex_plane_rollout_receipt.example.json",
    )
    assert all("aoa-sdk" not in ref for ref in bundle.source["receipt_input_paths"])


def test_live_mode_never_falls_back_to_available_reference_examples(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    facade = load_build_views_module()
    owner_root = tmp_path / "8Dionysus"
    workspace_root = tmp_path / "workspace"
    write_chain(owner_root, mode="reference")
    monkeypatch.setenv("AOA_8DIONYSUS_ROOT", str(owner_root))

    assert load_codex_plane_live_bundle(workspace_root) is None
    with pytest.raises(
        facade.ReceiptValidationError,
        match="missing Codex Plane live rollout artifacts",
    ):
        facade.build_codex_plane_deployment_summary(
            source_mode="live", workspace_root=workspace_root
        )


def test_partial_live_chain_is_not_completed_from_reference_examples(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / "workspace"
    trust_path, _, _ = codex_plane_live_paths(workspace_root)
    trust_path.parent.mkdir(parents=True)
    trust_path.write_text(json.dumps(trust_payload()), encoding="utf-8")

    with pytest.raises(
        codex_plane_deployment.ReceiptValidationError,
        match="missing Codex Plane regeneration report",
    ):
        load_codex_plane_live_bundle(workspace_root)


def test_valid_live_chain_uses_workspace_root_refs(tmp_path: Path) -> None:
    facade = load_build_views_module()
    workspace_root = tmp_path / "workspace"
    write_chain(workspace_root, mode="live")

    summary = facade.build_codex_plane_deployment_summary(
        source_mode="live", workspace_root=workspace_root
    )

    assert summary["generated_from"]["receipt_input_paths"] == [
        "workspace-root/.codex/generated/rollout/"
        "codex_plane_trust_state.current.json",
        "workspace-root/.codex/generated/rollout/"
        "codex_plane_regeneration_report.latest.json",
        "workspace-root/.codex/generated/rollout/"
        "codex_plane_rollout_receipt.latest.json",
    ]
    assert summary["latest_rollout_state"] == "verified"


def test_live_chain_must_declare_the_selected_workspace_root(tmp_path: Path) -> None:
    workspace_root = tmp_path / "selected-workspace"
    trust = trust_payload()
    regeneration = regeneration_payload()
    trust["workspace_root"] = "/srv/other-workspace"
    trust["detected_project_root"] = "/srv/other-workspace"
    regeneration["target_workspace_root"] = "/srv/other-workspace"
    write_chain(
        workspace_root,
        mode="live",
        trust=trust,
        regeneration=regeneration,
    )

    with pytest.raises(
        codex_plane_deployment.ReceiptValidationError,
        match="workspace_root must match the selected workspace root",
    ):
        load_codex_plane_live_bundle(workspace_root)


def test_build_all_views_omits_missing_live_chain_without_reference_fallback(
    tmp_path: Path,
) -> None:
    facade = load_build_views_module()
    receipts = facade.load_receipts([RECEIPT_FIXTURE])

    outputs = facade.build_all_views(
        receipts,
        ["stats/intake-contract/examples/session_harvest_family.receipts.example.json"],
        optional_output_names={"codex_plane_deployment_summary.min.json"},
        codex_plane_source_mode="live",
        codex_plane_workspace_root=tmp_path / "workspace",
    )

    assert "codex_plane_deployment_summary.min.json" not in outputs


def test_build_all_views_fails_on_invalid_live_chain(tmp_path: Path) -> None:
    facade = load_build_views_module()
    receipts = facade.load_receipts([RECEIPT_FIXTURE])
    workspace_root = tmp_path / "workspace"
    receipt = receipt_payload()
    receipt["trust_state_id"] = "wrong-trust"
    write_chain(workspace_root, mode="live", receipt=receipt)

    with pytest.raises(
        facade.ReceiptValidationError,
        match="must reference the loaded trust state",
    ):
        facade.build_all_views(
            receipts,
            [
                "stats/intake-contract/examples/"
                "session_harvest_family.receipts.example.json"
            ],
            optional_output_names={"codex_plane_deployment_summary.min.json"},
            codex_plane_source_mode="live",
            codex_plane_workspace_root=workspace_root,
        )


@pytest.mark.parametrize(
    ("mutate", "message"),
    (
        (
            lambda trust, regeneration, receipt: receipt.update(
                {"trust_state_id": "wrong-trust"}
            ),
            "must reference the loaded trust state",
        ),
        (
            lambda trust, regeneration, receipt: regeneration.update(
                {"target_workspace_root": "/srv/other"}
            ),
            "target must match the trust-state workspace root",
        ),
        (
            lambda trust, regeneration, receipt: regeneration.update(
                {"generated_at": "2026-04-11T22:00:00Z"}
            ),
            "timestamps must not postdate the rollout receipt",
        ),
        (
            lambda trust, regeneration, receipt: trust.update(
                {"captured_at": "2026-04-11"}
            ),
            "captured_at must be a date-time",
        ),
        (
            lambda trust, regeneration, receipt: receipt.update(
                {"doctor_result": "warn"}
            ),
            "verified deployment must keep doctor_result=pass",
        ),
        (
            lambda trust, regeneration, receipt: trust.update(
                {"unexpected": True}
            ),
            "unsupported fields: unexpected",
        ),
        (
            lambda trust, regeneration, receipt: trust.update(
                {"trust_posture": "config_inactive"}
            ),
            "config_inactive posture requires inactive project config",
        ),
        (
            lambda trust, regeneration, receipt: trust.update(
                {"detected_project_root": "/srv/wrong-root"}
            ),
            "trusted_ready posture contradicts its trust evidence",
        ),
        (
            lambda trust, regeneration, receipt: trust.update(
                {"trust_posture": "root_mismatch"}
            ),
            "root_mismatch posture requires an actual root mismatch",
        ),
    ),
)
def test_core_rejects_incoherent_or_invalid_owner_chains(mutate, message: str) -> None:
    trust = trust_payload()
    regeneration = regeneration_payload()
    receipt = receipt_payload()
    mutate(trust, regeneration, receipt)

    with pytest.raises(
        codex_plane_deployment.ReceiptValidationError,
        match=message,
    ):
        codex_plane_deployment.validate_codex_plane_deployment_chain(
            trust, regeneration, receipt
        )


def test_precursor_timestamps_may_follow_either_owner_documented_order() -> None:
    trust = trust_payload()
    trust["captured_at"] = "2026-04-11T21:05:00Z"
    regeneration = regeneration_payload()
    regeneration["generated_at"] = "2026-04-11T21:04:00Z"

    latest = codex_plane_deployment.validate_codex_plane_deployment_chain(
        trust, regeneration, receipt_payload()
    )

    assert latest.isoformat() == "2026-04-11T21:07:00+00:00"


def test_detected_project_mcp_superset_is_not_stable_name_drift() -> None:
    trust = trust_payload()
    trust["mcp_server_names_detected"].append("custom_project_mcp")

    summary = codex_plane_deployment.build_codex_plane_deployment_summary(
        source_payload(), trust, regeneration_payload(), receipt_payload()
    )

    assert summary["drift_count"] == 0
    assert summary["stable_mcp_name_set"] == sorted(
        codex_plane_deployment.CODEX_PLANE_V1_STABLE_MCP_NAMES
    )


def test_explicit_root_drift_drives_drift_and_rollback_counts() -> None:
    trust = trust_payload()
    trust["detected_project_root"] = "/srv/wrong-root"
    trust["trust_posture"] = "root_mismatch"

    summary = codex_plane_deployment.build_codex_plane_deployment_summary(
        source_payload(), trust, regeneration_payload(), receipt_payload()
    )

    assert summary["drift_count"] == 1
    assert summary["rollback_recommended_count"] == 1


def test_drifted_state_does_not_manufacture_rollback_recommendation() -> None:
    receipt = receipt_payload()
    receipt["deployment_state"] = "drifted"
    receipt["doctor_result"] = "warn"

    summary = codex_plane_deployment.build_codex_plane_deployment_summary(
        source_payload(), trust_payload(), regeneration_payload(), receipt
    )

    assert summary["drift_count"] == 1
    assert summary["rollback_recommended_count"] == 0


@pytest.mark.parametrize("deployment_state", ("render_only", "dry_run_ready"))
def test_doctor_failure_is_an_explicit_rollback_trigger(
    deployment_state: str,
) -> None:
    receipt = receipt_payload()
    receipt["deployment_state"] = deployment_state
    receipt["doctor_result"] = "fail"

    summary = codex_plane_deployment.build_codex_plane_deployment_summary(
        source_payload(), trust_payload(), regeneration_payload(), receipt
    )

    assert summary["rollback_recommended_count"] == 1


@pytest.mark.parametrize(
    "mutate_trust",
    (
        lambda trust: trust.update(
            {"hooks_enabled": False, "trust_posture": "unknown"}
        ),
        lambda trust: trust.update(
            {
                "mcp_server_names_detected": trust[
                    "mcp_server_names_detected"
                ][:-1],
                "stable_names_ok": False,
                "trust_posture": "unknown",
            }
        ),
    ),
)
def test_drifted_hook_or_name_evidence_routes_to_rerollout_not_rollback(
    mutate_trust,
) -> None:
    trust = trust_payload()
    mutate_trust(trust)
    receipt = receipt_payload()
    receipt["deployment_state"] = "drifted"
    receipt["doctor_result"] = "warn"

    summary = codex_plane_deployment.build_codex_plane_deployment_summary(
        source_payload(), trust, regeneration_payload(), receipt
    )

    assert summary["drift_count"] == 1
    assert summary["rollback_recommended_count"] == 0


@pytest.mark.parametrize("deployment_state", ("applied", "verified"))
def test_post_apply_hook_drift_is_a_rollback_trigger(deployment_state: str) -> None:
    trust = trust_payload()
    trust["hooks_enabled"] = False
    trust["trust_posture"] = "unknown"
    receipt = receipt_payload()
    receipt["deployment_state"] = deployment_state

    summary = codex_plane_deployment.build_codex_plane_deployment_summary(
        source_payload(), trust, regeneration_payload(), receipt
    )

    assert summary["rollback_recommended_count"] == 1


@pytest.mark.parametrize("deployment_state", ("render_only", "dry_run_ready"))
@pytest.mark.parametrize(
    "mutate_trust",
    (
        lambda trust: trust.update(
            {
                "detected_project_root": "/srv/wrong-root",
                "trust_posture": "root_mismatch",
            }
        ),
        lambda trust: trust.update(
            {"project_config_active": False, "trust_posture": "config_inactive"}
        ),
        lambda trust: trust.update(
            {"hooks_enabled": False, "trust_posture": "unknown"}
        ),
        lambda trust: trust.update(
            {
                "mcp_server_names_detected": trust[
                    "mcp_server_names_detected"
                ][:-1],
                "stable_names_ok": False,
                "trust_posture": "unknown",
            }
        ),
    ),
)
def test_pre_apply_drift_does_not_manufacture_rollback(
    deployment_state: str,
    mutate_trust,
) -> None:
    trust = trust_payload()
    mutate_trust(trust)
    receipt = receipt_payload()
    receipt["deployment_state"] = deployment_state
    receipt["doctor_result"] = "warn"

    summary = codex_plane_deployment.build_codex_plane_deployment_summary(
        source_payload(), trust, regeneration_payload(), receipt
    )

    assert summary["drift_count"] == 1
    assert summary["rollback_recommended_count"] == 0
