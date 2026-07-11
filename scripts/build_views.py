#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import AbstractSet, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.candidate_lifecycle import (  # noqa: E402
    build_candidate_lineage_summary,
    build_owner_landing_summary,
    build_supersession_drop_summary,
)
from aoa_stats_builder.component_refresh import (  # noqa: E402
    COMPONENT_REFRESH_COMPONENT_DRIFT_CLASSES as COMPONENT_REFRESH_COMPONENT_DRIFT_CLASSES,
    COMPONENT_REFRESH_CURRENT_STATUSES as COMPONENT_REFRESH_CURRENT_STATUSES,
    COMPONENT_REFRESH_DECISION_STATUSES as COMPONENT_REFRESH_DECISION_STATUSES,
    COMPONENT_REFRESH_ROUTE_CLASSES as COMPONENT_REFRESH_ROUTE_CLASSES,
    COMPONENT_REFRESH_SIGNAL_DRIFT_CLASSES as COMPONENT_REFRESH_SIGNAL_DRIFT_CLASSES,
    build_component_refresh_summary as build_component_refresh_summary_from_inputs,
    component_refresh_drift_classes as component_refresh_drift_classes,
    component_refresh_route_class as component_refresh_route_class,
    component_refresh_status as component_refresh_status,
    latest_component_hints_by_component as latest_component_hints_by_component,
)
from aoa_stats_builder.component_refresh_sources import (  # noqa: E402
    ComponentRefreshInputBundle,
    load_reviewed_sdk_example_bundle,
    reviewed_sdk_example_paths,
)
from aoa_stats_builder.codex_plane_deployment import (  # noqa: E402
    TRUST_POSTURES as TRUST_POSTURES,
    build_codex_plane_deployment_summary as build_codex_plane_deployment_summary_from_inputs,
)
from aoa_stats_builder.codex_plane_deployment_sources import (  # noqa: E402
    CODEX_PLANE_LIVE_ROLLOUT_ROOT,
    CodexPlaneDeploymentInputBundle,
    codex_plane_reference_paths,
    load_codex_plane_live_bundle,
    load_codex_plane_reference_bundle,
)
from aoa_stats_builder.codex_trusted_rollout import (  # noqa: E402
    build_codex_rollout_drift_summary as build_codex_rollout_drift_summary_from_inputs,
    build_codex_rollout_operations_summary as build_codex_rollout_operations_summary_from_inputs,
    latest_rollout_history_row as latest_rollout_history_row_from_inputs,
)
from aoa_stats_builder.codex_trusted_rollout_sources import (  # noqa: E402
    CodexTrustedRolloutInputBundle,
    codex_trusted_rollout_paths as codex_trusted_rollout_source_paths,
    load_codex_trusted_rollout_bundle,
)
from aoa_stats_builder.continuity_window import (  # noqa: E402
    CONTINUITY_EVAL_ANCHORS as CONTINUITY_EVAL_ANCHORS,
    CONTINUITY_STATUSES as CONTINUITY_STATUSES,
    build_continuity_window_summary as build_continuity_window_summary_from_inputs,
    continuity_drift_flags as continuity_drift_flags,
    continuity_reanchor_counts as continuity_reanchor_counts,
)
from aoa_stats_builder.continuity_window_sources import (  # noqa: E402
    ContinuityWindowInputBundle,
    continuity_window_reference_paths,
    load_continuity_window_reference_bundle,
)
from aoa_stats_builder.core_skill_observation import (  # noqa: E402
    build_core_skill_application_summary,
    build_surface_detection_summary,
    core_skill_identity as core_skill_identity,
    surface_detection_context as surface_detection_context,
)
from aoa_stats_builder.growth_cycle import (  # noqa: E402
    build_automation_followthrough_summary,
    build_automation_pipeline_summary,
    build_fork_calibration_summary,
    build_session_growth_branch_summary,
)
from aoa_stats_builder.memory_movement import (  # noqa: E402
    build_memory_movement_summary as build_memory_movement_summary_from_inputs,
)
from aoa_stats_builder.memory_movement_sources import (  # noqa: E402
    MemoryMovementInputBundle,
    load_memory_movement_bundle,
    memory_movement_source_paths as memory_movement_source_paths_from_root,
)
from aoa_stats_builder.object_observation import (  # noqa: E402
    build_object_summary,
    object_key,
)
from aoa_stats_builder.receipt_abi import (  # noqa: E402
    ReceiptValidationError,
    generated_from,
    load_receipts,
    resolve_active_receipts,
    validate_receipt as validate_receipt,
)
from aoa_stats_builder.read_model_values import is_nonempty_string  # noqa: E402
from aoa_stats_builder.repeated_window import (  # noqa: E402
    build_repeated_window_summary as build_repeated_window_summary_from_inputs,
)
from aoa_stats_builder.rollout_cadence import (  # noqa: E402
    build_drift_review_summary as build_drift_review_summary_from_inputs,
    build_rollout_campaign_summary as build_rollout_campaign_summary_from_inputs,
)
from aoa_stats_builder.rollout_cadence_sources import (  # noqa: E402
    RolloutCadenceInputBundle,
    load_rollout_cadence_reference_bundle,
    rollout_cadence_reference_paths,
)
from aoa_stats_builder.route_progression import (  # noqa: E402
    AXES as AXES,
    axis_template as axis_template,
    build_route_progression_summary,
)
from aoa_stats_builder.runtime_closeout import (  # noqa: E402
    build_runtime_closeout_summary as build_runtime_closeout_summary,
    runtime_closeout_identity as runtime_closeout_identity,
)
from aoa_stats_builder.source_coverage import build_source_coverage_summary  # noqa: E402
from aoa_stats_builder.stress_recovery import (  # noqa: E402
    build_stress_recovery_window_summary as build_stress_recovery_window_summary_from_inputs,
    latest_stress_recovery_report_ref,
)
from aoa_stats_builder.stress_recovery_sources import (  # noqa: E402
    load_stress_recovery_committed_reference_report,
)
from aoa_stats_builder.surface_catalog import build_summary_surface_catalog  # noqa: E402
from aoa_stats_builder.titan_observation import (  # noqa: E402
    build_titan_incarnation_summary as build_titan_incarnation_summary_from_inputs,
    build_titan_summon_no_observed_ledger_baseline,
)
from aoa_stats_builder.titan_observation_sources import (  # noqa: E402
    TitanIncarnationInputBundle,
    load_titan_incarnation_reference_bundle,
    titan_incarnation_reference_paths as titan_incarnation_source_paths_from_roots,
)

DEFAULT_INPUT = (
    REPO_ROOT
    / "stats"
    / "intake-contract"
    / "examples"
    / "session_harvest_family.receipts.example.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "generated"
LIVE_SOURCE_REGISTRY_RELATIVE = Path(
    "mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json"
)
DEFAULT_SOURCE_REGISTRY = REPO_ROOT / LIVE_SOURCE_REGISTRY_RELATIVE


def default_neighbor_root(repo_name: str, *, allow_nested: bool = False) -> Path:
    candidates = []
    if allow_nested:
        candidates.append(REPO_ROOT / repo_name)
    candidates.extend(
        [
            REPO_ROOT / ".deps" / repo_name,
            Path("/srv/AbyssOS") / repo_name,
            REPO_ROOT.parent / repo_name,
        ]
    )
    return next((candidate.resolve() for candidate in candidates if candidate.is_dir()), candidates[-1])


DEFAULT_EVALS_ROOT = default_neighbor_root("aoa-evals", allow_nested=True)
DEFAULT_PUBLIC_PROFILE_ROOT = default_neighbor_root("8Dionysus")
DEFAULT_AOA_AGENTS_ROOT = default_neighbor_root("aoa-agents")
DEFAULT_AOA_PLAYBOOKS_ROOT = default_neighbor_root("aoa-playbooks")
DEFAULT_AOA_MEMO_ROOT = default_neighbor_root("aoa-memo")
DEFAULT_AOA_SDK_ROOT = default_neighbor_root("aoa-sdk")

def repo_root_from_env(env_name: str, default: Path) -> Path:
    override = os.environ.get(env_name)
    if not override:
        return default
    return Path(override).expanduser().resolve()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build aoa-stats derived views.")
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help=(
            "Path to a JSON or JSONL file containing one receipt object, an array "
            "of receipt envelopes, or one JSON receipt envelope per line."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where generated summary JSON files should live.",
    )
    parser.add_argument(
        "--evals-root",
        default=str(repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT)),
        help="Path to the aoa-evals repository root used to resolve linked report_ref payloads.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that generated outputs are current instead of rewriting them.",
    )
    return parser.parse_args(argv)


def display_input_path(path: Path) -> str:
    for base in (REPO_ROOT, REPO_ROOT.parent):
        try:
            return str(path.relative_to(base))
        except ValueError:
            continue
    return str(path)


def display_repo_input_path(path: Path, *, repo_roots: tuple[tuple[str, Path], ...]) -> str:
    for repo_name, repo_root in repo_roots:
        try:
            relative_path = path.relative_to(repo_root)
        except ValueError:
            continue
        return f"{repo_name}/{relative_path.as_posix()}"
    return display_input_path(path)


def load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReceiptValidationError(f"invalid JSON in {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise ReceiptValidationError(f"{label} must be a JSON object: {path}")
    return payload


def codex_plane_example_paths() -> tuple[Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    return codex_plane_reference_paths(public_profile_root)


def codex_plane_input_bundle(
    *,
    source_mode: str = "reference",
    workspace_root: Path | None = None,
) -> CodexPlaneDeploymentInputBundle:
    if source_mode == "reference":
        public_profile_root = repo_root_from_env(
            "AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT
        )
        return load_codex_plane_reference_bundle(public_profile_root)
    if source_mode == "live":
        if workspace_root is None:
            raise ReceiptValidationError(
                "Codex Plane live source mode requires an explicit workspace root"
            )
        resolved_workspace_root = workspace_root.expanduser().resolve()
        bundle = load_codex_plane_live_bundle(resolved_workspace_root)
        if bundle is None:
            raise ReceiptValidationError(
                "missing Codex Plane live rollout artifacts: "
                f"{resolved_workspace_root / CODEX_PLANE_LIVE_ROLLOUT_ROOT}"
            )
        return bundle
    raise ReceiptValidationError(
        f"unsupported Codex Plane source mode: {source_mode!r}"
    )


def codex_plane_generated_from() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    """Preserve the legacy mutable tuple facade for compatibility callers."""

    return codex_plane_input_bundle().mutable_parts()


def codex_trusted_rollout_paths() -> tuple[Path, Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    return codex_trusted_rollout_source_paths(public_profile_root)


def codex_trusted_rollout_input_bundle() -> CodexTrustedRolloutInputBundle:
    public_profile_root = repo_root_from_env(
        "AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT
    )
    return load_codex_trusted_rollout_bundle(public_profile_root)


def codex_trusted_rollout_generated_from() -> tuple[
    dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    """Preserve the historical mutable five-part facade for callers."""

    return codex_trusted_rollout_input_bundle().mutable_parts()


def codex_rollout_campaign_paths() -> tuple[Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    return rollout_cadence_reference_paths(public_profile_root)


def rollout_cadence_input_bundle() -> RolloutCadenceInputBundle:
    public_profile_root = repo_root_from_env(
        "AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT
    )
    return load_rollout_cadence_reference_bundle(public_profile_root)


def codex_rollout_campaign_generated_from() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Preserve the historical mutable four-part facade for callers."""

    return rollout_cadence_input_bundle().mutable_parts()


def latest_rollout_history_row(
    deploy_history: list[dict[str, Any]], latest: dict[str, Any]
) -> dict[str, Any]:
    """Preserve the historical root helper while delegating to the pure core."""

    if not is_nonempty_string(latest.get("latest_rollout_campaign_ref")):
        return dict(deploy_history[-1])
    return dict(latest_rollout_history_row_from_inputs(deploy_history, latest))


def continuity_window_source_paths() -> tuple[Path, Path, Path, Path]:
    agents_root = repo_root_from_env("AOA_AGENTS_ROOT", DEFAULT_AOA_AGENTS_ROOT)
    playbooks_root = repo_root_from_env("AOA_PLAYBOOKS_ROOT", DEFAULT_AOA_PLAYBOOKS_ROOT)
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    evals_root = repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT)
    return continuity_window_reference_paths(
        agents_root=agents_root,
        playbooks_root=playbooks_root,
        memo_root=memo_root,
        evals_root=evals_root,
    )


def continuity_window_input_bundle() -> ContinuityWindowInputBundle:
    agents_root = repo_root_from_env("AOA_AGENTS_ROOT", DEFAULT_AOA_AGENTS_ROOT)
    playbooks_root = repo_root_from_env("AOA_PLAYBOOKS_ROOT", DEFAULT_AOA_PLAYBOOKS_ROOT)
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    evals_root = repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT)
    return load_continuity_window_reference_bundle(
        agents_root=agents_root,
        playbooks_root=playbooks_root,
        memo_root=memo_root,
        evals_root=evals_root,
    )

def continuity_window_generated_from() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Preserve the legacy mutable tuple facade for compatibility callers."""

    return continuity_window_input_bundle().mutable_parts()


def component_refresh_source_paths() -> tuple[Path, Path]:
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    return reviewed_sdk_example_paths(sdk_root)


def component_refresh_input_bundle() -> ComponentRefreshInputBundle:
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    return load_reviewed_sdk_example_bundle(sdk_root)


def titan_incarnation_source_paths() -> tuple[Path, Path, Path]:
    agents_root = repo_root_from_env("AOA_AGENTS_ROOT", DEFAULT_AOA_AGENTS_ROOT)
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    return titan_incarnation_source_paths_from_roots(
        agents_root=agents_root, sdk_root=sdk_root
    )


def titan_incarnation_input_bundle() -> TitanIncarnationInputBundle:
    agents_root = repo_root_from_env("AOA_AGENTS_ROOT", DEFAULT_AOA_AGENTS_ROOT)
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    return load_titan_incarnation_reference_bundle(
        agents_root=agents_root, sdk_root=sdk_root
    )


def component_refresh_generated_from() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Preserve the legacy mutable tuple facade for compatibility callers."""

    return component_refresh_input_bundle().mutable_parts()


def build_stress_recovery_window_summary(
    receipts: list[dict[str, Any]],
    source: dict[str, Any],
    *,
    evals_root: Path,
) -> dict[str, Any]:
    """Preserve the committed-reference root facade for compatibility callers."""

    report_ref = latest_stress_recovery_report_ref(receipts)
    report = load_stress_recovery_committed_reference_report(
        evals_root,
        report_ref,
    )
    return build_stress_recovery_window_summary_from_inputs(
        receipts,
        source,
        report=report,
    )


def build_repeated_window_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    """Preserve the root object-identity compatibility hook."""

    return build_repeated_window_summary_from_inputs(
        receipts,
        source,
        object_identity=object_key,
    )


def build_codex_plane_deployment_summary(
    *,
    source_mode: str = "reference",
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    bundle = codex_plane_input_bundle(
        source_mode=source_mode,
        workspace_root=workspace_root,
    )
    return build_codex_plane_deployment_summary_from_inputs(
        bundle.source,
        bundle.trust,
        bundle.regeneration,
        bundle.receipt,
    )


def build_codex_rollout_operations_summary() -> dict[str, Any]:
    bundle = codex_trusted_rollout_input_bundle()
    return build_codex_rollout_operations_summary_from_inputs(
        bundle.source,
        bundle.deploy_history,
        bundle.regeneration,
        bundle.rollback,
        bundle.latest,
    )


def build_codex_rollout_drift_summary() -> dict[str, Any]:
    bundle = codex_trusted_rollout_input_bundle()
    return build_codex_rollout_drift_summary_from_inputs(
        bundle.source,
        bundle.deploy_history,
        bundle.regeneration,
        bundle.rollback,
        bundle.latest,
    )


def build_rollout_campaign_summary() -> dict[str, Any]:
    bundle = rollout_cadence_input_bundle()
    return build_rollout_campaign_summary_from_inputs(
        bundle.source,
        bundle.campaign,
        bundle.review,
        bundle.rollback,
    )


def build_drift_review_summary() -> dict[str, Any]:
    bundle = rollout_cadence_input_bundle()
    return build_drift_review_summary_from_inputs(
        bundle.source,
        bundle.campaign,
        bundle.review,
        bundle.rollback,
    )


def build_continuity_window_summary() -> dict[str, Any]:
    bundle = continuity_window_input_bundle()
    return build_continuity_window_summary_from_inputs(
        bundle.source,
        bundle.continuity_window,
        bundle.memo_thread,
    )


def memory_movement_source_paths() -> tuple[Path, Path, Path, Path]:
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    return memory_movement_source_paths_from_root(memo_root)


def memory_movement_input_bundle() -> MemoryMovementInputBundle:
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    return load_memory_movement_bundle(memo_root)


def memory_movement_generated_from() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[tuple[Path, dict[str, Any]]],
    list[tuple[Path, dict[str, Any]]],
    list[tuple[Path, dict[str, Any]]],
]:
    """Preserve the historical mutable tuple facade for compatibility callers."""

    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    source, catalog, memory_objects, reviewed_intakes, landing_receipts = (
        memory_movement_input_bundle().mutable_parts()
    )
    catalog_objects = catalog.get("memory_objects")
    if not isinstance(catalog_objects, list):
        raise ReceiptValidationError(
            "aoa-memo memory object min catalog must expose memory_objects"
        )

    def restore_paths(
        values: list[tuple[str, dict[str, Any]]],
    ) -> list[tuple[Path, dict[str, Any]]]:
        return [
            (memo_root / ref.removeprefix("aoa-memo/"), payload)
            for ref, payload in values
        ]

    return (
        source,
        catalog_objects,
        restore_paths(memory_objects),
        restore_paths(reviewed_intakes),
        restore_paths(landing_receipts),
    )


def build_memory_movement_summary() -> dict[str, Any]:
    bundle = memory_movement_input_bundle()
    return build_memory_movement_summary_from_inputs(
        bundle.source,
        bundle.catalog,
        bundle.memory_objects,
        bundle.reviewed_intakes,
        bundle.landing_receipts,
    )


def build_component_refresh_summary() -> dict[str, Any]:
    bundle = component_refresh_input_bundle()
    return build_component_refresh_summary_from_inputs(
        bundle.source,
        bundle.hints,
        bundle.decisions,
    )


def build_titan_incarnation_summary() -> dict[str, Any]:
    bundle = titan_incarnation_input_bundle()
    return build_titan_incarnation_summary_from_inputs(
        bundle.operator_roster,
        bundle.runtime_roster,
        bundle.session_receipt,
        source_refs=bundle.source_refs,
    )


def build_titan_summon_summary() -> dict[str, Any]:
    return build_titan_summon_no_observed_ledger_baseline()


def build_all_views(
    receipts: list[dict[str, Any]],
    input_paths: list[str],
    *,
    evals_root: Path | None = None,
    source_registry: dict[str, Any] | None = None,
    source_registry_ref: str | None = None,
    optional_output_names: AbstractSet[str] | None = None,
    codex_plane_source_mode: str = "reference",
    codex_plane_workspace_root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    active_receipts = resolve_active_receipts(receipts)
    source = generated_from(active_receipts, input_paths)
    resolved_evals_root = (
        evals_root.expanduser().resolve()
        if evals_root is not None
        else repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT).resolve()
    )
    resolved_source_registry = source_registry
    resolved_source_registry_ref = source_registry_ref
    if resolved_source_registry is None and DEFAULT_SOURCE_REGISTRY.exists():
        resolved_source_registry = load_json_object(
            DEFAULT_SOURCE_REGISTRY,
            label=LIVE_SOURCE_REGISTRY_RELATIVE.as_posix(),
        )
        resolved_source_registry_ref = LIVE_SOURCE_REGISTRY_RELATIVE.as_posix()
    outputs = {
        "object_summary.min.json": build_object_summary(active_receipts, source),
        "candidate_lineage_summary.min.json": build_candidate_lineage_summary(
            active_receipts, source
        ),
        "supersession_drop_summary.min.json": build_supersession_drop_summary(
            active_receipts, source
        ),
        "core_skill_application_summary.min.json": build_core_skill_application_summary(
            active_receipts, source
        ),
        "repeated_window_summary.min.json": build_repeated_window_summary(active_receipts, source),
        "fork_calibration_summary.min.json": build_fork_calibration_summary(active_receipts, source),
        "session_growth_branch_summary.min.json": build_session_growth_branch_summary(
            active_receipts, source
        ),
        "automation_pipeline_summary.min.json": build_automation_pipeline_summary(
            active_receipts, source
        ),
        "automation_followthrough_summary.min.json": build_automation_followthrough_summary(
            active_receipts, source
        ),
        "source_coverage_summary.min.json": build_source_coverage_summary(
            active_receipts,
            source,
            source_registry=resolved_source_registry,
            source_registry_ref=resolved_source_registry_ref,
        ),
        "surface_detection_summary.min.json": build_surface_detection_summary(active_receipts, source),
    }
    allowed_optional_outputs = (
        None if optional_output_names is None else frozenset(optional_output_names)
    )

    def build_codex_plane_optional() -> dict[str, Any]:
        return build_codex_plane_deployment_summary(
            source_mode=codex_plane_source_mode,
            workspace_root=codex_plane_workspace_root,
        )

    for name, builder in (
        (
            "route_progression_summary.min.json",
            lambda: build_route_progression_summary(active_receipts, source),
        ),
        (
            "owner_landing_summary.min.json",
            lambda: build_owner_landing_summary(active_receipts, source),
        ),
        ("codex_plane_deployment_summary.min.json", build_codex_plane_optional),
        ("codex_rollout_operations_summary.min.json", build_codex_rollout_operations_summary),
        ("codex_rollout_drift_summary.min.json", build_codex_rollout_drift_summary),
        ("rollout_campaign_summary.min.json", build_rollout_campaign_summary),
        ("drift_review_summary.min.json", build_drift_review_summary),
        ("continuity_window_summary.min.json", build_continuity_window_summary),
        ("component_refresh_summary.min.json", build_component_refresh_summary),
        ("memory_movement_summary.min.json", build_memory_movement_summary),
        (
            "runtime_closeout_summary.min.json",
            lambda: build_runtime_closeout_summary(active_receipts, source),
        ),
        (
            "stress_recovery_window_summary.min.json",
            lambda: build_stress_recovery_window_summary(
                active_receipts,
                source,
                evals_root=resolved_evals_root,
            ),
        ),
        ("titan_incarnation_summary.min.json", build_titan_incarnation_summary),
        ("titan_summon_summary.min.json", build_titan_summon_summary),
    ):
        if allowed_optional_outputs is not None and name not in allowed_optional_outputs:
            continue
        try:
            outputs[name] = builder()
        except ReceiptValidationError as exc:
            if not str(exc).startswith("missing "):
                raise
    outputs["summary_surface_catalog.min.json"] = build_summary_surface_catalog(
        source,
        available_output_names=set(outputs),
    )
    return outputs


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_paths = [Path(path).expanduser().resolve() for path in args.input] or [DEFAULT_INPUT]
    output_dir = Path(args.output_dir).expanduser().resolve()
    evals_root = Path(args.evals_root).expanduser().resolve()
    receipts = load_receipts(input_paths)
    outputs = build_all_views(
        receipts,
        [display_input_path(path) for path in input_paths],
        evals_root=evals_root,
    )

    if args.check:
        mismatches: list[str] = []
        for name, payload in outputs.items():
            target = output_dir / name
            expected = stable_json(payload)
            if not target.exists() or target.read_text(encoding="utf-8") != expected:
                mismatches.append(name)
        if mismatches:
            print(
                "Generated views are out of date: " + ", ".join(sorted(mismatches)),
                file=sys.stderr,
            )
            return 1
        print("[ok] generated views are current")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        (output_dir / name).write_text(stable_json(payload), encoding="utf-8")
    print(f"[ok] wrote {len(outputs)} derived summary surfaces to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
