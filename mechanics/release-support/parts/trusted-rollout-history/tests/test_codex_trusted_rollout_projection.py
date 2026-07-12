from __future__ import annotations

import importlib.util
import json
import os
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any, Callable

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
BUILD_VIEWS_PATH = REPO_ROOT / "scripts/build_views.py"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import codex_trusted_rollout  # noqa: E402
from aoa_stats_builder.codex_trusted_rollout_sources import (  # noqa: E402
    CodexTrustedRolloutInputBundle,
    codex_trusted_rollout_paths,
    load_codex_trusted_rollout_bundle,
)


def resolve_owner_root() -> Path:
    candidates = (
        os.environ.get("AOA_8DIONYSUS_ROOT"),
        str(REPO_ROOT / ".deps" / "8Dionysus"),
        str(REPO_ROOT.parent / "8Dionysus"),
        "/srv/AbyssOS/8Dionysus",
    )
    for candidate in candidates:
        if candidate and (Path(candidate) / "generated/codex/rollout").is_dir():
            return Path(candidate).expanduser().resolve()
    raise RuntimeError("could not resolve the pinned 8Dionysus owner root")


def mutable_owner_parts() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    return load_codex_trusted_rollout_bundle(resolve_owner_root()).mutable_parts()


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def build_from_bundle(
    bundle: CodexTrustedRolloutInputBundle,
) -> tuple[dict[str, Any], dict[str, Any]]:
    args = (
        bundle.source,
        bundle.deploy_history,
        bundle.regeneration,
        bundle.rollback,
        bundle.latest,
    )
    return (
        codex_trusted_rollout.build_codex_rollout_operations_summary(*args),
        codex_trusted_rollout.build_codex_rollout_drift_summary(*args),
    )


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", BUILD_VIEWS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_root_facade_preserves_legacy_missing_latest_ref_fallback() -> None:
    facade = load_build_views_module()
    history = [
        {"rollout_campaign_ref": "ROLL-20260411-first-01"},
        {"rollout_campaign_ref": "ROLL-20260412-second-02"},
    ]

    with pytest.raises(
        codex_trusted_rollout.ReceiptValidationError,
        match="latest rollout campaign ref does not resolve inside deploy history",
    ):
        codex_trusted_rollout.latest_rollout_history_row(history, {})

    selected = facade.latest_rollout_history_row(history, {})

    assert selected == history[-1]
    assert selected is not history[-1]


def test_owner_bundle_preserves_all_four_public_output_bytes_and_schemas() -> None:
    bundle = load_codex_trusted_rollout_bundle(resolve_owner_root())
    operations, drift = build_from_bundle(bundle)

    output_pairs = (
        (
            operations,
            REPO_ROOT / "generated/codex_rollout_operations_summary.min.json",
            REPO_ROOT / "mechanics/release-support/parts/trusted-rollout-history/"
            "examples/codex_rollout_operations_summary.example.json",
            REPO_ROOT / "schemas/codex-rollout-operations-summary.schema.json",
        ),
        (
            drift,
            REPO_ROOT / "generated/codex_rollout_drift_summary.min.json",
            REPO_ROOT / "mechanics/release-support/parts/trusted-rollout-history/"
            "examples/codex_rollout_drift_summary.example.json",
            REPO_ROOT / "schemas/codex-rollout-drift-summary.schema.json",
        ),
    )
    for payload, generated_path, example_path, schema_path in output_pairs:
        expected = stable_json(payload)
        assert generated_path.read_text(encoding="utf-8") == expected
        assert example_path.read_text(encoding="utf-8") == expected
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(payload)


def test_adapter_uses_only_the_exact_checked_in_history_paths() -> None:
    owner_root = resolve_owner_root()
    paths = codex_trusted_rollout_paths(owner_root)
    bundle = load_codex_trusted_rollout_bundle(owner_root)

    assert tuple(path.relative_to(owner_root).as_posix() for path in paths) == (
        "generated/codex/rollout/deploy_history.jsonl",
        "generated/codex/rollout/regeneration_campaigns.min.json",
        "generated/codex/rollout/rollback_windows.min.json",
        "generated/codex/rollout/rollout_latest.min.json",
    )
    assert tuple(bundle.source["receipt_input_paths"]) == (
        "8Dionysus/generated/codex/rollout/deploy_history.jsonl",
        "8Dionysus/generated/codex/rollout/regeneration_campaigns.min.json",
        "8Dionysus/generated/codex/rollout/rollback_windows.min.json",
        "8Dionysus/generated/codex/rollout/rollout_latest.min.json",
    )
    assert bundle.source["total_receipts"] == len(bundle.deploy_history)
    assert bundle.source["latest_observed_at"] == "2026-04-11T21:36:00Z"


def test_input_bundle_is_deeply_immutable_and_mutable_tuple_is_detached() -> None:
    source, history, regeneration, rollback, latest = mutable_owner_parts()
    bundle = CodexTrustedRolloutInputBundle(
        source,
        history,
        regeneration,
        rollback,
        latest,
    )

    source["receipt_input_paths"].append("later")
    history[0]["state"] = "later"
    regeneration["campaigns"][0]["state"] = "later"
    mutable = bundle.mutable_parts()
    mutable[1][0]["state"] = "mutated-copy"

    assert len(bundle.source["receipt_input_paths"]) == 4
    assert bundle.deploy_history[0]["state"] == "stabilized"
    assert bundle.regeneration["campaigns"][0]["state"] == "stabilized"
    with pytest.raises(TypeError):
        bundle.latest["latest_state"] = "mutated"  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.deploy_history[0]["state"] = "mutated"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        bundle.source = {}  # type: ignore[misc]


def test_projection_core_is_filesystem_free_and_does_not_mutate_inputs() -> None:
    core_source = Path(codex_trusted_rollout.__file__).read_text(encoding="utf-8")
    assert "pathlib" not in core_source
    assert "read_text(" not in core_source
    assert "open(" not in core_source

    inputs = mutable_owner_parts()
    original = deepcopy(inputs)
    codex_trusted_rollout.build_codex_rollout_operations_summary(*inputs)
    codex_trusted_rollout.build_codex_rollout_drift_summary(*inputs)
    assert inputs == original


Mutation = Callable[
    [
        list[dict[str, Any]],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
    ],
    None,
]


@pytest.mark.parametrize(
    "mutate",
    (
        lambda history, regeneration, rollback, latest: history[0].update(
            {"schema_version": "wrong"}
        ),
        lambda history, regeneration, rollback, latest: history[0].update(
            {"deploy_receipt_refs": ["DEPLOY-20260411-other-01"]}
        ),
        lambda history, regeneration, rollback, latest: history[0].update(
            {"state": "unknown"}
        ),
        lambda history, regeneration, rollback, latest: history[0].update(
            {"drift_state": "unknown"}
        ),
        lambda history, regeneration, rollback, latest: history[0].update(
            {"repair_attempted": "false"}
        ),
        lambda history, regeneration, rollback, latest: history[0].update(
            {"activated_at": "not-a-date"}
        ),
        lambda history, regeneration, rollback, latest: regeneration.update(
            {"campaigns": regeneration["campaigns"][:-1]}
        ),
        lambda history, regeneration, rollback, latest: rollback.update(
            {"rollback_windows": []}
        ),
        lambda history, regeneration, rollback, latest: latest.update(
            {"latest_rollout_campaign_ref": history[0]["rollout_campaign_ref"]}
        ),
        lambda history, regeneration, rollback, latest: latest.update(
            {"latest_stable_rollout_campaign_ref": history[-1]["rollout_campaign_ref"]}
        ),
        lambda history, regeneration, rollback, latest: latest.update(
            {"source_refs": list(reversed(latest["source_refs"]))}
        ),
    ),
)
def test_core_rejects_owner_history_invariant_breaks(mutate: Mutation) -> None:
    _, history, regeneration, rollback, latest = mutable_owner_parts()
    mutate(history, regeneration, rollback, latest)

    with pytest.raises(codex_trusted_rollout.ReceiptValidationError):
        codex_trusted_rollout.validate_codex_trusted_rollout_chain(
            history,
            regeneration,
            rollback,
            latest,
        )


def test_prepared_history_entry_may_lack_an_activation_timestamp() -> None:
    _, history, regeneration, rollback, latest = mutable_owner_parts()
    prepared_ref = "ROLL-20260412-codex-next-pass-03"
    history.append(
        {
            "schema_version": "8dionysus_codex_trusted_rollout_entry_v1",
            "rollout_campaign_ref": prepared_ref,
            "state": "prepared",
            "activated_at": "",
            "actor": "codex+review",
            "scope": "next-bounded-pass",
            "deploy_receipt_refs": ["DEPLOY-20260412-codex-next-pass-03"],
            "drift_window_refs": ["DRIFT-20260412-codex-next-pass-03"],
            "rollback_window_refs": [],
            "drift_state": "watch",
            "repair_attempted": False,
            "summary": "Prepared but not activated.",
        }
    )
    regeneration["campaigns"].append({"rollout_campaign_ref": prepared_ref})
    latest.update(
        {
            "latest_rollout_campaign_ref": prepared_ref,
            "latest_state": "prepared",
            "active_drift_window_ref": "DRIFT-20260412-codex-next-pass-03",
            "active_rollback_window_ref": None,
        }
    )

    latest_observed_at = codex_trusted_rollout.validate_codex_trusted_rollout_chain(
        history,
        regeneration,
        rollback,
        latest,
    )

    assert latest_observed_at.isoformat().replace("+00:00", "Z") == (
        "2026-04-11T21:36:00Z"
    )


def test_core_rejects_generated_from_that_does_not_match_validated_history() -> None:
    source, history, regeneration, rollback, latest = mutable_owner_parts()
    source["total_receipts"] += 1

    with pytest.raises(
        codex_trusted_rollout.ReceiptValidationError,
        match="total_receipts must match deploy-history length",
    ):
        codex_trusted_rollout.build_codex_rollout_operations_summary(
            source,
            history,
            regeneration,
            rollback,
            latest,
        )


def test_adapter_rejects_malformed_jsonl_before_projection(tmp_path: Path) -> None:
    owner_root = tmp_path / "8Dionysus"
    source_root = resolve_owner_root()
    source_paths = codex_trusted_rollout_paths(source_root)
    target_paths = codex_trusted_rollout_paths(owner_root)
    for source_path, target_path in zip(source_paths, target_paths, strict=True):
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(source_path.read_bytes())
    target_paths[0].write_text("{not-json}\n", encoding="utf-8")

    with pytest.raises(
        codex_trusted_rollout.ReceiptValidationError,
        match="invalid JSON in Codex trusted rollout deploy history",
    ):
        load_codex_trusted_rollout_bundle(owner_root)
