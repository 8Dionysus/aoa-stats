#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "examples" / "session_harvest_family.receipts.example.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "generated"
DEFAULT_EVALS_ROOT = (
    REPO_ROOT / "aoa-evals"
    if (REPO_ROOT / "aoa-evals").exists()
    else (REPO_ROOT / ".deps" / "aoa-evals" if (REPO_ROOT / ".deps" / "aoa-evals").exists() else REPO_ROOT.parent / "aoa-evals")
)
DEFAULT_PUBLIC_PROFILE_ROOT = (
    REPO_ROOT / ".deps" / "8Dionysus"
    if (REPO_ROOT / ".deps" / "8Dionysus").exists()
    else REPO_ROOT.parent / "8Dionysus"
)
DEFAULT_AOA_AGENTS_ROOT = (
    REPO_ROOT / ".deps" / "aoa-agents"
    if (REPO_ROOT / ".deps" / "aoa-agents").exists()
    else REPO_ROOT.parent / "aoa-agents"
)
DEFAULT_AOA_PLAYBOOKS_ROOT = (
    REPO_ROOT / ".deps" / "aoa-playbooks"
    if (REPO_ROOT / ".deps" / "aoa-playbooks").exists()
    else REPO_ROOT.parent / "aoa-playbooks"
)
DEFAULT_AOA_MEMO_ROOT = (
    REPO_ROOT / ".deps" / "aoa-memo"
    if (REPO_ROOT / ".deps" / "aoa-memo").exists()
    else REPO_ROOT.parent / "aoa-memo"
)
DEFAULT_AOA_SDK_ROOT = (
    REPO_ROOT / ".deps" / "aoa-sdk"
    if (REPO_ROOT / ".deps" / "aoa-sdk").exists()
    else REPO_ROOT.parent / "aoa-sdk"
)
CANONICAL_ENVELOPE_SCHEMA_PATH = REPO_ROOT / "schemas" / "stats-event-envelope.schema.json"
CANONICAL_ENVELOPE_SCHEMA_REF = "schemas/stats-event-envelope.schema.json"

AXES = (
    "boundary_integrity",
    "execution_reliability",
    "change_legibility",
    "review_sharpness",
    "proof_discipline",
    "provenance_hygiene",
    "deep_readiness",
)
FUNNEL_STAGES = (
    "observed",
    "checkpointed",
    "reviewed",
    "harvested",
    "seeded",
    "planted",
    "proved",
    "promoted",
    "superseded_or_dropped",
)
TIME_TO_STAGE_KEYS = (
    "checkpointed",
    "reviewed",
    "harvested",
    "seeded",
    "planted",
    "proved",
    "promoted",
)
AMBIGUOUS_OWNER_TARGETS = {"hold", "unknown", "unresolved"}
OWNER_LANDING_OUTCOMES = (
    "landed_owner_status",
    "landed_owner_object",
    "reanchored",
    "merged",
    "deferred",
    "dropped",
)
FOLLOWTHROUGH_SKILL_NAMES = frozenset(
    {
        "aoa-session-route-forks",
        "aoa-session-self-diagnose",
        "aoa-session-self-repair",
        "aoa-session-progression-lift",
        "aoa-automation-opportunity-scan",
        "aoa-quest-harvest",
    }
)
TRUST_POSTURES = (
    "unknown",
    "root_mismatch",
    "config_inactive",
    "trusted_ready",
    "rollout_active",
    "rollback_recommended",
)
CONTINUITY_STATUSES = ("active", "reanchor_needed", "reanchored", "closed")
CONTINUITY_EVAL_ANCHORS = (
    "aoa-continuity-anchor-integrity",
    "aoa-reflective-revision-boundedness",
    "aoa-self-reanchor-correctness",
)


def repo_root_from_env(env_name: str, default: Path) -> Path:
    override = os.environ.get(env_name)
    if not override:
        return default
    return Path(override).expanduser().resolve()


class ReceiptValidationError(ValueError):
    pass


@lru_cache(maxsize=1)
def supported_event_kinds() -> frozenset[str]:
    payload = json.loads(CANONICAL_ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: canonical envelope schema must be a JSON object"
        )
    properties = payload.get("properties")
    if not isinstance(properties, dict):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: missing properties object"
        )
    event_kind = properties.get("event_kind")
    if not isinstance(event_kind, dict):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: missing properties.event_kind object"
        )
    enum = event_kind.get("enum")
    if not isinstance(enum, list) or not enum:
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: properties.event_kind.enum must be a non-empty list"
        )
    supported = {item for item in enum if isinstance(item, str) and item}
    if len(supported) != len(enum):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: properties.event_kind.enum must contain only non-empty strings"
        )
    return frozenset(supported)


def automation_pipeline_ref(receipt: dict[str, Any]) -> str:
    payload = receipt["payload"]
    for key in ("pipeline_ref", "manual_route_ref"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return receipt["session_ref"]


def fork_option_count(payload: dict[str, Any]) -> int:
    option_count = payload.get("branch_options_count")
    if isinstance(option_count, int) and option_count > 0:
        return option_count
    branch_ids = payload.get("branch_ids")
    if isinstance(branch_ids, list):
        return len([branch_id for branch_id in branch_ids if isinstance(branch_id, str) and branch_id])
    return 0


def runtime_closeout_identity(receipt: dict[str, Any]) -> tuple[str, str]:
    payload = receipt["payload"]
    program_id = payload.get("program_id")
    wave_id = payload.get("wave_id")
    if isinstance(program_id, str) and program_id and isinstance(wave_id, str) and wave_id:
        return program_id, wave_id
    object_id = str(receipt["object_ref"].get("id") or "")
    if ":" in object_id:
        fallback_program_id, fallback_wave_id = object_id.rsplit(":", 1)
        return fallback_program_id or "unknown-program", fallback_wave_id or "unknown-wave"
    return "unknown-program", receipt["session_ref"]


def core_skill_identity(receipt: dict[str, Any]) -> tuple[str, str]:
    payload = receipt["payload"]
    kernel_id = payload.get("kernel_id")
    skill_name = payload.get("skill_name")
    if isinstance(kernel_id, str) and kernel_id and isinstance(skill_name, str) and skill_name:
        return kernel_id, skill_name
    object_id = receipt["object_ref"].get("id")
    if isinstance(object_id, str) and object_id:
        return "unknown-kernel", object_id
    return "unknown-kernel", "unknown-skill"


def surface_detection_context(receipt: dict[str, Any]) -> dict[str, Any]:
    payload = receipt["payload"]
    context = payload.get("surface_detection_context")
    if not isinstance(context, dict):
        return {}
    return context


def receipt_sort_key(receipt: dict[str, Any]) -> tuple[str, str]:
    return receipt["observed_at"], receipt["event_id"]


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
        default=str(DEFAULT_EVALS_ROOT),
        help="Path to the aoa-evals repository root used to resolve linked report_ref payloads.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that generated outputs are current instead of rewriting them.",
    )
    return parser.parse_args(argv)


def load_receipts(paths: list[Path]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for path in paths:
        if path.suffix == ".jsonl":
            receipts.extend(load_receipts_from_jsonl(path))
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            validate_receipt(payload, location=str(path))
            receipts.append(payload)
            continue
        if not isinstance(payload, list):
            raise ReceiptValidationError(f"{path}: receipt feed must be a JSON object or array")
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ReceiptValidationError(f"{path}[{index}]: receipt must be an object")
            validate_receipt(item, location=f"{path}[{index}]")
            receipts.append(item)
    deduped: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        deduped[receipt["event_id"]] = receipt
    return sorted(deduped.values(), key=receipt_sort_key)


def load_receipts_from_jsonl(path: Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReceiptValidationError(
                f"{path}:{line_number}: invalid JSONL receipt line"
            ) from exc
        if not isinstance(item, dict):
            raise ReceiptValidationError(f"{path}:{line_number}: receipt must be an object")
        validate_receipt(item, location=f"{path}:{line_number}")
        receipts.append(item)
    return receipts


def validate_receipt(receipt: dict[str, Any], *, location: str) -> None:
    required_fields = (
        "event_kind",
        "event_id",
        "observed_at",
        "run_ref",
        "session_ref",
        "actor_ref",
        "object_ref",
        "evidence_refs",
        "payload",
    )
    for field in required_fields:
        if field not in receipt:
            raise ReceiptValidationError(f"{location}: missing field '{field}'")

    for field in ("event_kind", "event_id", "run_ref", "session_ref", "actor_ref"):
        if not isinstance(receipt[field], str) or not receipt[field]:
            raise ReceiptValidationError(f"{location}.{field}: must be a non-empty string")
    if receipt["event_kind"] not in supported_event_kinds():
        raise ReceiptValidationError(
            f"{location}.event_kind: unsupported event kind {receipt['event_kind']!r}; "
            f"see {CANONICAL_ENVELOPE_SCHEMA_REF}"
        )

    try:
        datetime.fromisoformat(receipt["observed_at"].replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ReceiptValidationError(
            f"{location}.observed_at: must be an ISO datetime"
        ) from exc

    object_ref = receipt["object_ref"]
    if not isinstance(object_ref, dict):
        raise ReceiptValidationError(f"{location}.object_ref: must be an object")
    for field in ("repo", "kind", "id"):
        if not isinstance(object_ref.get(field), str) or not object_ref[field]:
            raise ReceiptValidationError(
                f"{location}.object_ref.{field}: must be a non-empty string"
            )

    evidence_refs = receipt["evidence_refs"]
    if not isinstance(evidence_refs, list):
        raise ReceiptValidationError(f"{location}.evidence_refs: must be a list")
    for index, item in enumerate(evidence_refs):
        if not isinstance(item, dict):
            raise ReceiptValidationError(
                f"{location}.evidence_refs[{index}]: must be an object"
            )
        for field in ("kind", "ref"):
            if not isinstance(item.get(field), str) or not item[field]:
                raise ReceiptValidationError(
                    f"{location}.evidence_refs[{index}].{field}: must be a non-empty string"
                )

    if not isinstance(receipt["payload"], dict):
        raise ReceiptValidationError(f"{location}.payload: must be an object")
    supersedes = receipt.get("supersedes")
    if supersedes is not None and (not isinstance(supersedes, str) or not supersedes):
        raise ReceiptValidationError(f"{location}.supersedes: must be omitted or a non-empty string")


def resolve_active_receipts(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    receipt_by_id = {receipt["event_id"]: receipt for receipt in receipts}
    supersedes_by_id = {
        receipt["event_id"]: receipt["supersedes"]
        for receipt in receipts
        if isinstance(receipt.get("supersedes"), str)
        and receipt["supersedes"] in receipt_by_id
        and receipt["supersedes"] != receipt["event_id"]
    }
    cycle_nodes = find_supersedes_cycle_nodes(supersedes_by_id)
    effective_supersedes = {
        event_id: target_id
        for event_id, target_id in supersedes_by_id.items()
        if event_id not in cycle_nodes and target_id not in cycle_nodes
    }

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        family_root = resolve_receipt_family_root(
            receipt["event_id"], effective_supersedes
        )
        grouped[family_root].append(receipt)

    active = [
        max(group, key=receipt_sort_key)
        for group in grouped.values()
    ]
    return sorted(active, key=receipt_sort_key)


def find_supersedes_cycle_nodes(supersedes_by_id: dict[str, str]) -> set[str]:
    cycle_nodes: set[str] = set()
    seen_done: set[str] = set()

    for start in supersedes_by_id:
        if start in seen_done:
            continue
        order: list[str] = []
        positions: dict[str, int] = {}
        current = start
        while current in supersedes_by_id:
            if current in seen_done:
                break
            if current in positions:
                cycle_nodes.update(order[positions[current] :])
                break
            positions[current] = len(order)
            order.append(current)
            current = supersedes_by_id[current]
        seen_done.update(order)

    return cycle_nodes


def resolve_receipt_family_root(event_id: str, supersedes_by_id: dict[str, str]) -> str:
    current = event_id
    while current in supersedes_by_id:
        current = supersedes_by_id[current]
    return current


def generated_from(receipts: list[dict[str, Any]], input_paths: list[str]) -> dict[str, Any]:
    latest_observed_at = max(receipt["observed_at"] for receipt in receipts)
    return {
        "receipt_input_paths": input_paths,
        "total_receipts": len(receipts),
        "latest_observed_at": latest_observed_at,
    }


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_iso_datetime(value: Any) -> datetime | None:
    if not is_nonempty_string(value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if is_nonempty_string(item)]


def parse_iso_datetime_or_min(value: Any) -> datetime:
    parsed = parse_iso_datetime(value)
    if parsed is None:
        return datetime.min.replace(tzinfo=UTC)
    return parsed


def summary_window_ref(receipts: list[dict[str, Any]]) -> str:
    months = sorted(
        {
            parsed.strftime("%Y-%m")
            for receipt in receipts
            if (parsed := parse_iso_datetime(receipt.get("observed_at"))) is not None
        }
    )
    if not months:
        return "window:unknown"
    if len(months) == 1:
        return f"window:{months[0]}"
    return f"window:{months[0]}..{months[-1]}"


def string_count_map(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


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


def load_jsonl_objects(path: Path, *, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc

    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReceiptValidationError(
                f"invalid JSON line in {label}: {path}:{line_number}"
            ) from exc
        if not isinstance(payload, dict):
            raise ReceiptValidationError(
                f"{label} entries must be JSON objects: {path}:{line_number}"
            )
        rows.append(payload)
    if not rows:
        raise ReceiptValidationError(f"{label} must expose at least one JSON object: {path}")
    return rows


def load_text_surface(path: Path, *, label: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc
    if not text.strip():
        raise ReceiptValidationError(f"{label} must not be empty: {path}")
    return text


def codex_plane_example_paths() -> tuple[Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    return (
        public_profile_root / "examples" / "codex_plane_trust_state.example.json",
        sdk_root / "examples" / "codex_plane_deploy_status_snapshot.example.json",
        public_profile_root / "examples" / "codex_plane_rollout_receipt.example.json",
    )


def codex_plane_generated_from() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    trust_path, status_path, receipt_path = codex_plane_example_paths()
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    sdk_root = repo_root_from_env("AOA_SDK_ROOT", DEFAULT_AOA_SDK_ROOT)
    trust = load_json_object(trust_path, label="codex plane trust-state example")
    status = load_json_object(status_path, label="codex plane deploy-status example")
    receipt = load_json_object(receipt_path, label="codex plane rollout receipt example")
    latest_observed_at = max(
        parse_iso_datetime_or_min(trust.get("captured_at")),
        parse_iso_datetime_or_min(status.get("observed_at")),
        parse_iso_datetime_or_min(receipt.get("verified_at")),
    ).isoformat().replace("+00:00", "Z")
    source = {
        "receipt_input_paths": [
            display_repo_input_path(
                trust_path,
                repo_roots=(("8Dionysus", public_profile_root), ("aoa-sdk", sdk_root)),
            ),
            display_repo_input_path(
                status_path,
                repo_roots=(("8Dionysus", public_profile_root), ("aoa-sdk", sdk_root)),
            ),
            display_repo_input_path(
                receipt_path,
                repo_roots=(("8Dionysus", public_profile_root), ("aoa-sdk", sdk_root)),
            ),
        ],
        "total_receipts": 1,
        "latest_observed_at": latest_observed_at,
    }
    return source, trust, status, receipt


def codex_trusted_rollout_paths() -> tuple[Path, Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    rollout_root = public_profile_root / "generated" / "codex" / "rollout"
    return (
        rollout_root / "deploy_history.jsonl",
        rollout_root / "regeneration_campaigns.min.json",
        rollout_root / "rollback_windows.min.json",
        rollout_root / "rollout_latest.min.json",
    )


def codex_trusted_rollout_generated_from() -> tuple[
    dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    (
        deploy_history_path,
        regeneration_path,
        rollback_path,
        latest_path,
    ) = codex_trusted_rollout_paths()
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    deploy_history = load_jsonl_objects(
        deploy_history_path,
        label="codex trusted rollout deploy history",
    )
    regeneration = load_json_object(
        regeneration_path,
        label="codex trusted rollout regeneration campaigns",
    )
    rollback = load_json_object(
        rollback_path,
        label="codex trusted rollout rollback windows",
    )
    latest = load_json_object(
        latest_path,
        label="codex trusted rollout latest summary",
    )
    observed_candidates = [
        parse_iso_datetime_or_min(row.get("activated_at"))
        for row in deploy_history
    ]
    rollback_windows = rollback.get("rollback_windows")
    if isinstance(rollback_windows, list):
        observed_candidates.extend(
            parse_iso_datetime_or_min(item.get("closed_at"))
            for item in rollback_windows
            if isinstance(item, dict)
        )
    latest_observed_at = max(observed_candidates).isoformat().replace("+00:00", "Z")
    source = {
        "receipt_input_paths": [
            display_repo_input_path(
                deploy_history_path,
                repo_roots=(("8Dionysus", public_profile_root),),
            ),
            display_repo_input_path(
                regeneration_path,
                repo_roots=(("8Dionysus", public_profile_root),),
            ),
            display_repo_input_path(
                rollback_path,
                repo_roots=(("8Dionysus", public_profile_root),),
            ),
            display_repo_input_path(
                latest_path,
                repo_roots=(("8Dionysus", public_profile_root),),
            ),
        ],
        "total_receipts": len(deploy_history),
        "latest_observed_at": latest_observed_at,
    }
    return source, deploy_history, regeneration, rollback, latest


def codex_rollout_campaign_paths() -> tuple[Path, Path, Path]:
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    return (
        public_profile_root / "examples" / "rollout_campaign_window.example.json",
        public_profile_root / "examples" / "drift_review_window.example.json",
        public_profile_root / "examples" / "rollback_followthrough_window.example.json",
    )


def codex_rollout_campaign_generated_from() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    campaign_path, review_path, rollback_path = codex_rollout_campaign_paths()
    public_profile_root = repo_root_from_env("AOA_8DIONYSUS_ROOT", DEFAULT_PUBLIC_PROFILE_ROOT)
    campaign = load_json_object(campaign_path, label="rollout campaign window example")
    review = load_json_object(review_path, label="drift review window example")
    rollback = load_json_object(rollback_path, label="rollback followthrough window example")
    latest_observed_at = max(
        parse_iso_datetime_or_min(campaign.get("window_opened_at")),
        parse_iso_datetime_or_min(review.get("reviewed_at")),
        parse_iso_datetime_or_min(rollback.get("prepared_at")),
    ).isoformat().replace("+00:00", "Z")
    source = {
        "receipt_input_paths": [
            display_repo_input_path(campaign_path, repo_roots=(("8Dionysus", public_profile_root),)),
            display_repo_input_path(review_path, repo_roots=(("8Dionysus", public_profile_root),)),
            display_repo_input_path(rollback_path, repo_roots=(("8Dionysus", public_profile_root),)),
        ],
        "total_receipts": 1,
        "latest_observed_at": latest_observed_at,
    }
    return source, campaign, review, rollback


def continuity_window_source_paths() -> tuple[Path, Path, Path, Path]:
    agents_root = repo_root_from_env("AOA_AGENTS_ROOT", DEFAULT_AOA_AGENTS_ROOT)
    playbooks_root = repo_root_from_env("AOA_PLAYBOOKS_ROOT", DEFAULT_AOA_PLAYBOOKS_ROOT)
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    evals_root = repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT)
    return (
        agents_root
        / "examples"
        / "self_agent_checkpoint"
        / "self_agency_continuity_window.example.json",
        playbooks_root / "playbooks" / "self-agency-continuity-cycle" / "PLAYBOOK.md",
        memo_root / "examples" / "provenance_thread.self-agency-continuity.example.json",
        evals_root / "generated" / "eval_catalog.min.json",
    )


def continuity_window_generated_from() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    continuity_path, playbook_path, memo_path, eval_catalog_path = continuity_window_source_paths()
    agents_root = repo_root_from_env("AOA_AGENTS_ROOT", DEFAULT_AOA_AGENTS_ROOT)
    playbooks_root = repo_root_from_env("AOA_PLAYBOOKS_ROOT", DEFAULT_AOA_PLAYBOOKS_ROOT)
    memo_root = repo_root_from_env("AOA_MEMO_ROOT", DEFAULT_AOA_MEMO_ROOT)
    evals_root = repo_root_from_env("AOA_EVALS_ROOT", DEFAULT_EVALS_ROOT)

    continuity_window = load_json_object(
        continuity_path,
        label="self-agency continuity window example",
    )
    playbook_text = load_text_surface(
        playbook_path,
        label="self-agency continuity playbook",
    )
    memo_thread = load_json_object(
        memo_path,
        label="self-agency continuity provenance thread example",
    )
    eval_catalog = load_json_object(
        eval_catalog_path,
        label="continuity eval catalog",
    )

    continuity_ref = continuity_window.get("continuity_ref")
    revision_window_ref = continuity_window.get("revision_window_ref")
    anchor_artifact_ref = continuity_window.get("anchor_artifact_ref")
    current_status = continuity_window.get("continuity_status")

    if continuity_window.get("schema_version") != "self_agency_continuity_window_v1":
        raise ReceiptValidationError(
            "self-agency continuity window example must keep schema_version self_agency_continuity_window_v1"
        )
    if not is_nonempty_string(continuity_ref):
        raise ReceiptValidationError("self-agency continuity window example must expose continuity_ref")
    if not is_nonempty_string(revision_window_ref):
        raise ReceiptValidationError(
            "self-agency continuity window example must expose revision_window_ref"
        )
    if not is_nonempty_string(anchor_artifact_ref):
        raise ReceiptValidationError(
            "self-agency continuity window example must expose anchor_artifact_ref"
        )
    if current_status not in CONTINUITY_STATUSES:
        raise ReceiptValidationError(
            "self-agency continuity window example must keep continuity_status inside the published grammar"
        )
    if memo_thread.get("continuity_ref") != continuity_ref:
        raise ReceiptValidationError(
            "self-agency continuity provenance thread must preserve the continuity_ref from aoa-agents"
        )
    if memo_thread.get("revision_window_ref") != revision_window_ref:
        raise ReceiptValidationError(
            "self-agency continuity provenance thread must preserve the revision_window_ref from aoa-agents"
        )
    if memo_thread.get("anchor_artifact_ref") != anchor_artifact_ref:
        raise ReceiptValidationError(
            "self-agency continuity provenance thread must preserve the anchor_artifact_ref from aoa-agents"
        )
    for token in (
        "AOA-P-0029",
        "continuity_window",
        "reanchor_decision",
        "continuity_writeback_record",
    ):
        if token not in playbook_text:
            raise ReceiptValidationError(
                f"self-agency continuity playbook must mention {token}"
            )
    eval_entries = eval_catalog.get("evals")
    if not isinstance(eval_entries, list):
        raise ReceiptValidationError("continuity eval catalog must expose evals")
    eval_names = {
        item.get("name")
        for item in eval_entries
        if isinstance(item, dict) and is_nonempty_string(item.get("name"))
    }
    missing_eval_names = [
        name for name in CONTINUITY_EVAL_ANCHORS if name not in eval_names
    ]
    if missing_eval_names:
        raise ReceiptValidationError(
            "continuity eval catalog is missing continuity anchors: "
            + ", ".join(missing_eval_names)
        )

    timeline = memo_thread.get("timeline")
    if not isinstance(timeline, list) or not timeline:
        raise ReceiptValidationError(
            "self-agency continuity provenance thread must expose a non-empty timeline"
        )
    latest_observed_at = max(
        parse_iso_datetime_or_min(item.get("at"))
        for item in timeline
        if isinstance(item, dict)
    ).isoformat().replace("+00:00", "Z")
    repo_roots = (
        ("aoa-agents", agents_root),
        ("aoa-playbooks", playbooks_root),
        ("aoa-memo", memo_root),
        ("aoa-evals", evals_root),
    )
    source = {
        "receipt_input_paths": [
            display_repo_input_path(continuity_path, repo_roots=repo_roots),
            display_repo_input_path(playbook_path, repo_roots=repo_roots),
            display_repo_input_path(memo_path, repo_roots=repo_roots),
            display_repo_input_path(eval_catalog_path, repo_roots=repo_roots),
        ],
        "total_receipts": 1,
        "latest_observed_at": latest_observed_at,
    }
    return source, continuity_window, memo_thread


def continuity_reanchor_counts(
    memo_thread: dict[str, Any], current_status: str
) -> tuple[int, int]:
    successful = 0
    failed = 0
    timeline = memo_thread.get("timeline")
    if not isinstance(timeline, list):
        return successful, failed
    for item in timeline:
        if not isinstance(item, dict):
            continue
        text = " ".join(str(item.get(key) or "") for key in ("action", "note")).lower()
        if "failed reanchor" in text or "reanchor failed" in text:
            failed += 1
            continue
        if "reanchor" in text and any(
            token in text for token in ("captured", "recorded", "completed", "returned")
        ):
            successful += 1
    if current_status == "reanchored" and successful == 0:
        successful = 1
    return successful, failed


def continuity_drift_flags(current_status: str, failed_reanchors: int) -> list[str]:
    flags: list[str] = []
    if current_status == "reanchor_needed":
        flags.append("reanchor_needed")
    if failed_reanchors > 0:
        flags.append("failed_reanchor_present")
    return flags


def normalized_code_list(value: Any) -> list[str]:
    return [
        item.strip()
        for item in normalize_string_list(value)
        if is_nonempty_string(item) and item.strip()
    ]


def followthrough_recommended_next_skill(payload: dict[str, Any]) -> str | None:
    recommended = payload.get("recommended_next_skill")
    if isinstance(recommended, str) and recommended in FOLLOWTHROUGH_SKILL_NAMES:
        return recommended
    chosen_branch = payload.get("chosen_branch")
    if isinstance(chosen_branch, str) and chosen_branch in FOLLOWTHROUGH_SKILL_NAMES:
        return chosen_branch
    return None


def automation_blocker_codes(payload: dict[str, Any]) -> list[str]:
    blocker_codes = normalized_code_list(payload.get("blocker_codes"))
    if blocker_codes:
        return blocker_codes
    return normalized_code_list(payload.get("blockers"))


def ensure_repo_relative_ref_path(raw_path: str) -> str | None:
    if not is_nonempty_string(raw_path):
        return None
    normalized = raw_path.strip().replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("./"):
        return None
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return normalized


def resolve_repo_ref_path(raw_ref: Any, repo_roots: dict[str, Path]) -> Path | None:
    if not is_nonempty_string(raw_ref):
        return None
    ref = raw_ref.strip()
    if not ref.startswith("repo:"):
        return None
    repo_and_path = ref[len("repo:") :]
    repo_name, separator, relative_path = repo_and_path.partition("/")
    if not separator or repo_name not in repo_roots:
        return None
    normalized = ensure_repo_relative_ref_path(relative_path)
    if normalized is None:
        return None
    return repo_roots[repo_name] / Path(normalized)


def load_optional_json_object(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def stress_summary_template() -> dict[str, Any]:
    return {
        "containment": None,
        "route_discipline": None,
        "reentry_quality": None,
        "regrounding_effectiveness": None,
        "evidence_continuity": None,
        "adaptation_followthrough": None,
        "operator_burden": None,
        "trust_calibration": None,
    }


def empty_stress_counts() -> dict[str, int]:
    return {
        "receipt_count": 0,
        "handoff_count": 0,
        "playbook_lane_count": 0,
        "reentry_gate_count": 0,
        "projection_health_count": 0,
        "regrounding_ticket_count": 0,
        "eval_count": 0,
    }


def report_axis_score(report: dict[str, Any], axis_name: str) -> float | None:
    axes = report.get("axes")
    if not isinstance(axes, dict):
        return None
    axis = axes.get(axis_name)
    if not isinstance(axis, dict):
        return None
    score = axis.get("score")
    if not is_number(score):
        return None
    return round(float(score), 2)


def average_scores(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return round(sum(present) / len(present), 2)


def latest_or_source_time(receipts: list[dict[str, Any]], source: dict[str, Any]) -> str:
    if receipts:
        return max(receipt["observed_at"] for receipt in receipts)
    return str(source.get("latest_observed_at") or "1970-01-01T00:00:00Z")


def build_suppressed_stress_recovery_window_summary(
    receipts: list[dict[str, Any]],
    source: dict[str, Any],
    *,
    status: str,
    reason: str,
) -> dict[str, Any]:
    observed_at = latest_or_source_time(receipts, source)
    trend_flags = ["stress-recovery-window-unavailable"]
    if status == "low_sample":
        trend_flags = ["low-sample-window"]
    return {
        "schema_version": "aoa_stats_stress_recovery_window_summary_v1",
        "generated_from": source,
        "window": {
            "label": "stress-recovery-window-unavailable",
            "start_utc": observed_at,
            "end_utc": observed_at,
        },
        "scope": {
            "repo_family": ["aoa-evals"],
            "stressor_family": "unresolved",
            "owner_surface": None,
            "surface_family": None,
        },
        "inputs": {
            "receipt_refs": [],
            "eval_report_refs": [],
            "route_hint_refs": [],
            "memo_context_refs": [],
        },
        "counts": empty_stress_counts(),
        "suppression": {
            "status": status,
            "reason": reason,
        },
        "summary": stress_summary_template(),
        "trend_flags": trend_flags,
    }


def build_stress_recovery_window_metrics(
    report: dict[str, Any],
    *,
    suppression_status: str,
) -> dict[str, Any]:
    if suppression_status != "none":
        return stress_summary_template()

    reentry_quality = report_axis_score(report, "reentry_quality")
    regrounding_effectiveness = report_axis_score(report, "regrounding_effectiveness")
    operator_burden = report_axis_score(report, "operator_burden")
    return {
        "containment": report_axis_score(report, "handoff_fidelity"),
        "route_discipline": report_axis_score(report, "route_discipline"),
        "reentry_quality": reentry_quality,
        "regrounding_effectiveness": regrounding_effectiveness,
        "evidence_continuity": report_axis_score(report, "evidence_continuity"),
        "adaptation_followthrough": average_scores(
            [reentry_quality, regrounding_effectiveness, operator_burden]
        ),
        "operator_burden": operator_burden,
        "trust_calibration": report_axis_score(report, "trust_calibration"),
    }


def build_stress_recovery_window_summary(
    receipts: list[dict[str, Any]],
    source: dict[str, Any],
    *,
    evals_root: Path,
) -> dict[str, Any]:
    relevant_receipts = [
        receipt
        for receipt in receipts
        if receipt["event_kind"] == "eval_result_receipt"
        and isinstance(receipt.get("payload"), dict)
        and receipt["payload"].get("eval_name") == "aoa-stress-recovery-window"
    ]
    if not relevant_receipts:
        return build_suppressed_stress_recovery_window_summary(
            receipts,
            source,
            status="insufficient_evidence",
            reason="no aoa-stress-recovery-window eval_result_receipt was found in the active receipt feed",
        )

    latest_receipt = max(relevant_receipts, key=receipt_sort_key)
    payload = latest_receipt["payload"]
    report_ref = payload.get("report_ref")
    report_path = resolve_repo_ref_path(report_ref, {"aoa-evals": evals_root})
    report = load_optional_json_object(report_path)
    if report is None:
        return build_suppressed_stress_recovery_window_summary(
            relevant_receipts,
            source,
            status="insufficient_evidence",
            reason="report_ref for aoa-stress-recovery-window could not be resolved into a readable aoa-evals JSON report",
        )

    window = report.get("window")
    scope = report.get("scope")
    inputs = report.get("inputs")
    if not isinstance(window, dict) or not isinstance(scope, dict) or not isinstance(inputs, dict):
        return build_suppressed_stress_recovery_window_summary(
            relevant_receipts,
            source,
            status="insufficient_evidence",
            reason="resolved aoa-stress-recovery-window report is missing required window, scope, or inputs objects",
        )

    counts = {
        "receipt_count": len([item for item in inputs.get("source_receipt_refs", []) if is_nonempty_string(item)]),
        "handoff_count": len([item for item in inputs.get("handoff_refs", []) if is_nonempty_string(item)]),
        "playbook_lane_count": len([item for item in inputs.get("playbook_lane_refs", []) if is_nonempty_string(item)]),
        "reentry_gate_count": len([item for item in inputs.get("reentry_gate_refs", []) if is_nonempty_string(item)]),
        "projection_health_count": len([item for item in inputs.get("projection_health_refs", []) if is_nonempty_string(item)]),
        "regrounding_ticket_count": len([item for item in inputs.get("regrounding_ticket_refs", []) if is_nonempty_string(item)]),
        "eval_count": 1,
    }

    adjacent_signal_count = (
        counts["handoff_count"]
        + counts["playbook_lane_count"]
        + counts["reentry_gate_count"]
        + counts["projection_health_count"]
        + counts["regrounding_ticket_count"]
    )
    suppression_status = "none"
    suppression_reason: str | None = None
    if counts["receipt_count"] < 1:
        suppression_status = "insufficient_evidence"
        suppression_reason = "owner receipts are missing from the resolved stress recovery window report"
    elif counts["receipt_count"] < 2 or adjacent_signal_count < 4:
        suppression_status = "low_sample"
        suppression_reason = (
            "owner and adjacent stress signals stay too sparse for a confident repeated-window derived read"
        )

    report_refs = [report_ref] if is_nonempty_string(report_ref) else []
    route_hint_refs = [
        item for item in inputs.get("route_hint_refs", []) if is_nonempty_string(item)
    ]
    memo_context_refs = [
        item for item in inputs.get("memo_context_refs", []) if is_nonempty_string(item)
    ]

    trend_flags: list[str] = []
    overall_posture = report.get("overall_posture")
    if isinstance(overall_posture, str) and overall_posture:
        trend_flags.append(f"overall-posture-{overall_posture}")
    if suppression_status == "low_sample":
        trend_flags.append("low-sample-window")
    elif suppression_status == "insufficient_evidence":
        trend_flags.append("insufficient-evidence-window")
    if report_axis_score(report, "false_promotion_prevention") is not None:
        score = report_axis_score(report, "false_promotion_prevention")
        if score is not None and score >= 0.8:
            trend_flags.append("false-promotion-guard-held")

    return {
        "schema_version": "aoa_stats_stress_recovery_window_summary_v1",
        "generated_from": source,
        "window": {
            "label": str(window.get("label") or "stress-recovery-window"),
            "start_utc": str(window.get("start_utc") or source["latest_observed_at"]),
            "end_utc": str(window.get("end_utc") or source["latest_observed_at"]),
        },
        "scope": {
            "repo_family": [
                item for item in scope.get("repo_roots", []) if is_nonempty_string(item)
            ]
            or ["aoa-evals"],
            "stressor_family": str(scope.get("stressor_family") or "unresolved"),
            "owner_surface": scope.get("owner_surface")
            if scope.get("owner_surface") is None or is_nonempty_string(scope.get("owner_surface"))
            else None,
            "surface_family": scope.get("surface_family")
            if scope.get("surface_family") is None or is_nonempty_string(scope.get("surface_family"))
            else None,
        },
        "inputs": {
            "receipt_refs": [
                item for item in inputs.get("source_receipt_refs", []) if is_nonempty_string(item)
            ],
            "eval_report_refs": report_refs,
            "route_hint_refs": route_hint_refs,
            "memo_context_refs": memo_context_refs,
        },
        "counts": counts,
        "suppression": {
            "status": suppression_status,
            "reason": suppression_reason,
        },
        "summary": build_stress_recovery_window_metrics(
            report, suppression_status=suppression_status
        ),
        "trend_flags": trend_flags,
    }


def object_key(object_ref: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        object_ref["repo"],
        object_ref["kind"],
        object_ref["id"],
        object_ref.get("version", ""),
    )


def build_object_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        grouped[object_key(receipt["object_ref"])].append(receipt)

    objects: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        by_kind = Counter(receipt["event_kind"] for receipt in group)
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        latest_eval = None
        latest_progression = None
        automation_total = 0
        automation_seed_ready = 0
        automation_checkpoint_required = 0
        for receipt in group:
            payload = receipt["payload"]
            if receipt["event_kind"] == "eval_result_receipt":
                latest_eval = payload.get("verdict")
            if receipt["event_kind"] == "progression_delta_receipt":
                latest_progression = payload.get("verdict")
            if receipt["event_kind"] == "automation_candidate_receipt":
                automation_total += 1
                if payload.get("seed_ready") is True:
                    automation_seed_ready += 1
                if payload.get("checkpoint_required") is True:
                    automation_checkpoint_required += 1

        object_ref = dict(latest["object_ref"])
        objects.append(
            {
                "object_ref": object_ref,
                "receipt_count_total": len(group),
                "receipt_counts_by_event_kind": dict(sorted(by_kind.items())),
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": latest["observed_at"],
                "latest_session_ref": latest["session_ref"],
                "latest_run_ref": latest["run_ref"],
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "latest_eval_verdict": latest_eval,
                "latest_progression_verdict": latest_progression,
                "automation_candidate_counts": {
                    "total": automation_total,
                    "seed_ready": automation_seed_ready,
                    "checkpoint_required": automation_checkpoint_required,
                },
            }
        )

    return {
        "schema_version": "aoa_stats_object_summary_v1",
        "generated_from": source,
        "objects": objects,
    }


def empty_stage_counts() -> dict[str, int]:
    return {stage: 0 for stage in FUNNEL_STAGES}


def empty_time_to_stage() -> dict[str, float | None]:
    return {stage: None for stage in TIME_TO_STAGE_KEYS}


def normalize_lineage_stages(raw_stages: Any, *, fallback_observed_at: str) -> dict[str, str | None]:
    stages = {stage: None for stage in FUNNEL_STAGES}
    if isinstance(raw_stages, dict):
        for stage in FUNNEL_STAGES:
            timestamp = raw_stages.get(stage)
            if parse_iso_datetime(timestamp) is not None:
                stages[stage] = str(timestamp)
    if stages["observed"] is None and parse_iso_datetime(fallback_observed_at) is not None:
        stages["observed"] = fallback_observed_at
    return stages


def lineage_latest_datetime(entry: dict[str, Any]) -> datetime:
    latest = parse_iso_datetime(entry.get("receipt_observed_at"))
    for timestamp in entry["stages"].values():
        current = parse_iso_datetime(timestamp)
        if current is not None and (latest is None or current > latest):
            latest = current
    return latest or datetime.min


def collect_candidate_lineage_entries(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest_by_candidate: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        if receipt["event_kind"] != "harvest_packet_receipt":
            continue
        payload = receipt["payload"]
        evidence_density = payload.get("evidence_density_summary") or payload.get("evidence_density")
        if evidence_density != "reviewed":
            continue
        raw_entries = payload.get("candidate_lineage_entries")
        if not isinstance(raw_entries, list):
            continue
        for item in raw_entries:
            if not isinstance(item, dict):
                continue
            candidate_ref = item.get("candidate_ref")
            if not is_nonempty_string(candidate_ref):
                continue
            owner_hypothesis = item.get("owner_hypothesis")
            owner_shape = item.get("owner_shape")
            status_posture = item.get("status_posture")
            if not (
                is_nonempty_string(owner_hypothesis)
                and is_nonempty_string(owner_shape)
                and is_nonempty_string(status_posture)
            ):
                continue
            normalized = {
                "candidate_ref": candidate_ref,
                "cluster_ref": item.get("cluster_ref") if is_nonempty_string(item.get("cluster_ref")) else None,
                "owner_hypothesis": owner_hypothesis,
                "owner_shape": owner_shape,
                "nearest_wrong_target": (
                    item.get("nearest_wrong_target")
                    if is_nonempty_string(item.get("nearest_wrong_target"))
                    else None
                ),
                "status_posture": status_posture,
                "axis_pressure": normalize_string_list(item.get("axis_pressure")),
                "supersedes": normalize_string_list(item.get("supersedes")),
                "merged_into": item.get("merged_into") if is_nonempty_string(item.get("merged_into")) else None,
                "drop_reason": item.get("drop_reason") if is_nonempty_string(item.get("drop_reason")) else None,
                "evidence_refs": normalize_string_list(item.get("evidence_refs")),
                "stages": normalize_lineage_stages(item.get("stages"), fallback_observed_at=receipt["observed_at"]),
                "receipt_observed_at": receipt["observed_at"],
            }
            previous = latest_by_candidate.get(candidate_ref)
            if previous is None or lineage_latest_datetime(normalized) >= lineage_latest_datetime(previous):
                latest_by_candidate[candidate_ref] = normalized
    return sorted(
        latest_by_candidate.values(),
        key=lambda entry: (lineage_latest_datetime(entry), entry["candidate_ref"]),
    )


def median_days(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(median(values)), 2)


def stage_duration_days(entry: dict[str, Any], stage: str) -> float | None:
    observed = parse_iso_datetime(entry["stages"].get("observed"))
    target = parse_iso_datetime(entry["stages"].get(stage))
    if observed is None or target is None or target < observed:
        return None
    return (target - observed).total_seconds() / 86400


def build_candidate_lineage_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    entries = collect_candidate_lineage_entries(receipts)
    stage_counts = empty_stage_counts()
    owner_target_counts: Counter[str] = Counter()
    owner_shape_counts: Counter[str] = Counter()
    status_posture_counts: Counter[str] = Counter()
    misroute_target_counts: Counter[str] = Counter()
    axis_pressure_counts: Counter[str] = Counter()
    time_to_stage_values: dict[str, list[float]] = {stage: [] for stage in TIME_TO_STAGE_KEYS}
    owner_ambiguity_total = 0
    superseded_total = 0
    dropped_total = 0

    for entry in entries:
        for stage in FUNNEL_STAGES:
            if entry["stages"].get(stage) is not None:
                stage_counts[stage] += 1

        owner_target_counts[entry["owner_hypothesis"]] += 1
        owner_shape_counts[entry["owner_shape"]] += 1
        status_posture_counts[entry["status_posture"]] += 1
        if entry["owner_hypothesis"] in AMBIGUOUS_OWNER_TARGETS:
            owner_ambiguity_total += 1

        if entry["drop_reason"] is not None:
            dropped_total += 1
            if entry["nearest_wrong_target"] is not None:
                misroute_target_counts[entry["nearest_wrong_target"]] += 1
        if entry["merged_into"] is not None or entry["supersedes"]:
            superseded_total += 1

        for axis in entry["axis_pressure"]:
            axis_pressure_counts[axis] += 1
        for stage in TIME_TO_STAGE_KEYS:
            duration = stage_duration_days(entry, stage)
            if duration is not None:
                time_to_stage_values[stage].append(duration)

    return {
        "schema_version": "aoa_stats_candidate_lineage_summary_v1",
        "generated_from": source,
        "stage_counts": stage_counts,
        "owner_target_counts": dict(sorted(owner_target_counts.items())),
        "owner_shape_counts": dict(sorted(owner_shape_counts.items())),
        "status_posture_counts": dict(sorted(status_posture_counts.items())),
        "time_to_stage_median_days": {
            stage: median_days(values) for stage, values in time_to_stage_values.items()
        },
        "misroute_counts": {
            "total": sum(misroute_target_counts.values()),
            "by_target": dict(sorted(misroute_target_counts.items())),
            "owner_ambiguity_total": owner_ambiguity_total,
        },
        "supersession_counts": {
            "superseded_total": superseded_total,
            "dropped_total": dropped_total,
        },
        "axis_pressure_counts": dict(sorted(axis_pressure_counts.items())),
    }


def normalize_owner_landing_bundle(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    candidate_ref = payload.get("candidate_ref")
    owner_repo = payload.get("owner_repo")
    owner_shape = payload.get("owner_shape")
    status_posture = payload.get("status_posture")
    reviewed_at = payload.get("reviewed_at")
    evidence_refs = normalize_string_list(payload.get("evidence_refs"))
    if not (
        is_nonempty_string(candidate_ref)
        and is_nonempty_string(owner_repo)
        and is_nonempty_string(owner_shape)
        and is_nonempty_string(status_posture)
        and parse_iso_datetime(reviewed_at) is not None
        and evidence_refs
    ):
        return None
    return {
        "candidate_ref": candidate_ref,
        "cluster_ref": payload.get("cluster_ref") if is_nonempty_string(payload.get("cluster_ref")) else None,
        "owner_repo": owner_repo,
        "owner_shape": owner_shape,
        "nearest_wrong_target": (
            payload.get("nearest_wrong_target")
            if is_nonempty_string(payload.get("nearest_wrong_target"))
            else None
        ),
        "status_posture": status_posture,
        "reviewed_at": reviewed_at,
        "evidence_refs": evidence_refs,
        "status_note": payload.get("status_note") if is_nonempty_string(payload.get("status_note")) else None,
        "supersedes": normalize_string_list(payload.get("supersedes")),
        "superseded_by": (
            payload.get("superseded_by")
            if is_nonempty_string(payload.get("superseded_by"))
            else None
        ),
        "merged_into": (
            payload.get("merged_into")
            if is_nonempty_string(payload.get("merged_into"))
            else None
        ),
        "drop_reason": (
            payload.get("drop_reason")
            if is_nonempty_string(payload.get("drop_reason"))
            else None
        ),
        "drop_stage": payload.get("drop_stage") if is_nonempty_string(payload.get("drop_stage")) else None,
        "drop_evidence_refs": normalize_string_list(payload.get("drop_evidence_refs")),
    }


def collect_owner_landing_bundles(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest_by_candidate: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        if receipt["event_kind"] != "reviewed_owner_landing_receipt":
            continue
        normalized = normalize_owner_landing_bundle(receipt.get("payload"))
        if normalized is None:
            continue
        candidate_ref = normalized["candidate_ref"]
        previous = latest_by_candidate.get(candidate_ref)
        if previous is None or parse_iso_datetime_or_min(normalized["reviewed_at"]) >= parse_iso_datetime_or_min(
            previous["reviewed_at"]
        ):
            latest_by_candidate[candidate_ref] = normalized
    return sorted(
        latest_by_candidate.values(),
        key=lambda item: (parse_iso_datetime_or_min(item["reviewed_at"]), item["candidate_ref"]),
    )


def normalize_seed_owner_landing_trace(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    candidate_ref = payload.get("candidate_ref")
    seed_ref = payload.get("seed_ref")
    owner_repo = payload.get("owner_repo")
    owner_shape = payload.get("owner_shape")
    outcome = payload.get("outcome")
    observed_at = payload.get("observed_at")
    evidence_refs = normalize_string_list(payload.get("evidence_refs"))
    if not (
        is_nonempty_string(candidate_ref)
        and is_nonempty_string(seed_ref)
        and is_nonempty_string(owner_repo)
        and is_nonempty_string(owner_shape)
        and is_nonempty_string(outcome)
        and parse_iso_datetime(observed_at) is not None
        and evidence_refs
    ):
        return None
    return {
        "candidate_ref": candidate_ref,
        "cluster_ref": payload.get("cluster_ref") if is_nonempty_string(payload.get("cluster_ref")) else None,
        "seed_ref": seed_ref,
        "owner_repo": owner_repo,
        "owner_shape": owner_shape,
        "outcome": outcome,
        "owner_status_ref": (
            payload.get("owner_status_ref")
            if is_nonempty_string(payload.get("owner_status_ref"))
            else None
        ),
        "object_ref": payload.get("object_ref") if is_nonempty_string(payload.get("object_ref")) else None,
        "merged_into": (
            payload.get("merged_into")
            if is_nonempty_string(payload.get("merged_into"))
            else None
        ),
        "superseded_by": (
            payload.get("superseded_by")
            if is_nonempty_string(payload.get("superseded_by"))
            else None
        ),
        "drop_reason": (
            payload.get("drop_reason")
            if is_nonempty_string(payload.get("drop_reason"))
            else None
        ),
        "observed_at": observed_at,
        "evidence_refs": evidence_refs,
    }


def collect_seed_owner_landing_traces(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest_by_candidate: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        if receipt["event_kind"] != "seed_owner_landing_trace_receipt":
            continue
        normalized = normalize_seed_owner_landing_trace(receipt.get("payload"))
        if normalized is None:
            continue
        candidate_ref = normalized["candidate_ref"]
        previous = latest_by_candidate.get(candidate_ref)
        if previous is None or parse_iso_datetime_or_min(normalized["observed_at"]) >= parse_iso_datetime_or_min(
            previous["observed_at"]
        ):
            latest_by_candidate[candidate_ref] = normalized
    return sorted(
        latest_by_candidate.values(),
        key=lambda item: (parse_iso_datetime_or_min(item["observed_at"]), item["candidate_ref"]),
    )


def empty_owner_landing_time_to_outcome() -> dict[str, float | None]:
    return {outcome: None for outcome in OWNER_LANDING_OUTCOMES}


def duration_days_between(start_value: Any, end_value: Any) -> float | None:
    start = parse_iso_datetime(start_value)
    end = parse_iso_datetime(end_value)
    if start is None or end is None or end < start:
        return None
    return (end - start).total_seconds() / 86400


def build_owner_landing_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    bundle_states = collect_owner_landing_bundles(receipts)
    trace_states = collect_seed_owner_landing_traces(receipts)
    states: dict[str, dict[str, Any]] = {}

    for bundle in bundle_states:
        state = states.setdefault(
            bundle["candidate_ref"],
            {
                "owner_repo": None,
                "owner_shape": None,
                "status_posture": None,
                "first_reviewed_at": None,
                "landing_outcome": None,
                "landing_observed_at": None,
            },
        )
        state["owner_repo"] = bundle["owner_repo"]
        state["owner_shape"] = bundle["owner_shape"]
        state["status_posture"] = bundle["status_posture"]
        first_reviewed_at = state["first_reviewed_at"]
        if first_reviewed_at is None or parse_iso_datetime_or_min(bundle["reviewed_at"]) < parse_iso_datetime_or_min(
            first_reviewed_at
        ):
            state["first_reviewed_at"] = bundle["reviewed_at"]

    for trace in trace_states:
        state = states.setdefault(
            trace["candidate_ref"],
            {
                "owner_repo": None,
                "owner_shape": None,
                "status_posture": None,
                "first_reviewed_at": None,
                "landing_outcome": None,
                "landing_observed_at": None,
            },
        )
        state["owner_repo"] = trace["owner_repo"]
        state["owner_shape"] = trace["owner_shape"]
        state["landing_outcome"] = trace["outcome"]
        state["landing_observed_at"] = trace["observed_at"]

    owner_repo_counts: Counter[str] = Counter()
    owner_shape_counts: Counter[str] = Counter()
    status_posture_counts: Counter[str] = Counter()
    landing_outcome_counts: Counter[str] = Counter()
    time_to_outcome_values: dict[str, list[float]] = {outcome: [] for outcome in OWNER_LANDING_OUTCOMES}

    for state in states.values():
        owner_repo = state["owner_repo"]
        owner_shape = state["owner_shape"]
        status_posture = state["status_posture"]
        landing_outcome = state["landing_outcome"]
        if is_nonempty_string(owner_repo):
            owner_repo_counts[owner_repo] += 1
        if is_nonempty_string(owner_shape):
            owner_shape_counts[owner_shape] += 1
        if is_nonempty_string(status_posture):
            status_posture_counts[status_posture] += 1
        if is_nonempty_string(landing_outcome):
            landing_outcome_counts[landing_outcome] += 1
            duration = duration_days_between(state["first_reviewed_at"], state["landing_observed_at"])
            if duration is not None:
                time_to_outcome_values[landing_outcome].append(duration)

    return {
        "schema_version": "aoa_stats_owner_landing_summary_v1",
        "generated_from": source,
        "owner_repo_counts": dict(sorted(owner_repo_counts.items())),
        "owner_shape_counts": dict(sorted(owner_shape_counts.items())),
        "status_posture_counts": dict(sorted(status_posture_counts.items())),
        "landing_outcome_counts": dict(sorted(landing_outcome_counts.items())),
        "time_to_outcome_median_days": {
            outcome: median_days(values) for outcome, values in time_to_outcome_values.items()
        },
    }


def collect_turnover_records(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for entry in collect_candidate_lineage_entries(receipts):
        records.append(
            {
                "candidate_ref": entry["candidate_ref"],
                "owner_repo": entry["owner_hypothesis"],
                "owner_shape": entry["owner_shape"],
                "status_posture": entry["status_posture"],
                "drop_reason": entry["drop_reason"],
                "merged_into": entry["merged_into"],
                "superseded_by": None,
                "supersedes": entry["supersedes"],
                "outcome": None,
                "timestamp": entry["stages"].get("superseded_or_dropped")
                or entry["stages"].get("harvested")
                or entry["receipt_observed_at"],
            }
        )
    for bundle in collect_owner_landing_bundles(receipts):
        records.append(
            {
                "candidate_ref": bundle["candidate_ref"],
                "owner_repo": bundle["owner_repo"],
                "owner_shape": bundle["owner_shape"],
                "status_posture": bundle["status_posture"],
                "drop_reason": bundle["drop_reason"],
                "merged_into": bundle["merged_into"],
                "superseded_by": bundle["superseded_by"],
                "supersedes": bundle["supersedes"],
                "outcome": None,
                "timestamp": bundle["reviewed_at"],
            }
        )
    for trace in collect_seed_owner_landing_traces(receipts):
        records.append(
            {
                "candidate_ref": trace["candidate_ref"],
                "owner_repo": trace["owner_repo"],
                "owner_shape": trace["owner_shape"],
                "status_posture": None,
                "drop_reason": trace["drop_reason"],
                "merged_into": trace["merged_into"],
                "superseded_by": trace["superseded_by"],
                "supersedes": [],
                "outcome": trace["outcome"],
                "timestamp": trace["observed_at"],
            }
        )
    return sorted(
        records,
        key=lambda item: (parse_iso_datetime_or_min(item["timestamp"]), item["candidate_ref"]),
    )


def build_supersession_drop_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    states: dict[str, dict[str, Any]] = {}
    for record in collect_turnover_records(receipts):
        state = states.setdefault(
            record["candidate_ref"],
            {
                "owner_repo": None,
                "owner_shape": None,
                "status_posture": None,
                "drop_reason": None,
                "merged_into": None,
                "superseded_by": None,
                "supersedes": set(),
                "reanchor_after_drop": False,
            },
        )
        state["owner_repo"] = record["owner_repo"]
        state["owner_shape"] = record["owner_shape"]
        if is_nonempty_string(record["status_posture"]):
            state["status_posture"] = record["status_posture"]
        if is_nonempty_string(record["drop_reason"]):
            state["drop_reason"] = record["drop_reason"]
        if is_nonempty_string(record["merged_into"]):
            state["merged_into"] = record["merged_into"]
        if is_nonempty_string(record["superseded_by"]):
            state["superseded_by"] = record["superseded_by"]
        state["supersedes"].update(record["supersedes"])
        if is_nonempty_string(record["drop_reason"]) and (
            record["status_posture"] == "reanchor" or record["outcome"] == "reanchored"
        ):
            state["reanchor_after_drop"] = True

    drop_reason_counts: Counter[str] = Counter()
    owner_repo_counts: Counter[str] = Counter()
    merge_owner_repo_counts: Counter[str] = Counter()
    reanchor_after_drop_counts: Counter[str] = Counter()
    superseded_total = 0
    replacing_total = 0
    dropped_total = 0
    merge_total = 0

    for state in states.values():
        has_turnover = bool(
            state["drop_reason"]
            or state["merged_into"]
            or state["superseded_by"]
            or state["supersedes"]
            or state["reanchor_after_drop"]
        )
        if not has_turnover:
            continue
        owner_repo = state["owner_repo"]
        if is_nonempty_string(owner_repo):
            owner_repo_counts[owner_repo] += 1
        if is_nonempty_string(state["drop_reason"]):
            drop_reason_counts[state["drop_reason"]] += 1
            dropped_total += 1
        if is_nonempty_string(state["superseded_by"]):
            superseded_total += 1
        if state["supersedes"]:
            replacing_total += 1
        if is_nonempty_string(state["merged_into"]):
            merge_total += 1
            if is_nonempty_string(owner_repo):
                merge_owner_repo_counts[owner_repo] += 1
        if state["reanchor_after_drop"] and is_nonempty_string(owner_repo):
            reanchor_after_drop_counts[owner_repo] += 1

    return {
        "schema_version": "aoa_stats_supersession_drop_summary_v1",
        "generated_from": source,
        "drop_reason_counts": dict(sorted(drop_reason_counts.items())),
        "supersession_counts": {
            "superseded_total": superseded_total,
            "replacing_total": replacing_total,
            "dropped_total": dropped_total,
        },
        "merge_counts": {
            "total": merge_total,
            "by_owner_repo": dict(sorted(merge_owner_repo_counts.items())),
        },
        "owner_repo_counts": dict(sorted(owner_repo_counts.items())),
        "reanchor_after_drop_counts": dict(sorted(reanchor_after_drop_counts.items())),
    }


def build_core_skill_application_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "core_skill_application_receipt":
            continue
        payload = receipt.get("payload")
        if not isinstance(payload, dict) or payload.get("application_stage") != "finish":
            continue
        grouped[core_skill_identity(receipt)].append(receipt)

    skills: list[dict[str, Any]] = []
    for key in sorted(grouped):
        kernel_id, skill_name = key
        group = grouped[key]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        detail_counts: Counter[str] = Counter()
        for receipt in group:
            detail_event_kind = receipt["payload"].get("detail_event_kind")
            if isinstance(detail_event_kind, str) and detail_event_kind:
                detail_counts[detail_event_kind] += 1
        skills.append(
            {
                "kernel_id": kernel_id,
                "skill_name": skill_name,
                "application_count": len(group),
                "latest_observed_at": latest["observed_at"],
                "latest_session_ref": latest["session_ref"],
                "latest_run_ref": latest["run_ref"],
                "detail_event_kind_counts": dict(sorted(detail_counts.items())),
            }
        )

    return {
        "schema_version": "aoa_stats_core_skill_application_summary_v1",
        "generated_from": source,
        "skills": skills,
    }


def build_repeated_window_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        grouped[receipt["observed_at"][:10]].append(receipt)

    windows: list[dict[str, Any]] = []
    for window_date in sorted(grouped):
        group = grouped[window_date]
        event_counts = Counter(receipt["event_kind"] for receipt in group)
        unique_objects = {object_key(receipt["object_ref"]) for receipt in group}
        windows.append(
            {
                "window_id": f"window:{window_date}",
                "window_date": window_date,
                "total_receipts": len(group),
                "unique_objects": len(unique_objects),
                "event_counts_by_kind": dict(sorted(event_counts.items())),
                "eval_result_count": event_counts.get("eval_result_receipt", 0),
                "progression_delta_count": event_counts.get("progression_delta_receipt", 0),
                "automation_candidate_count": event_counts.get(
                    "automation_candidate_receipt", 0
                ),
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
            }
        )

    return {
        "schema_version": "aoa_stats_repeated_window_summary_v1",
        "generated_from": source,
        "windows": windows,
    }


def axis_template() -> dict[str, int]:
    return {axis: 0 for axis in AXES}


def build_route_progression_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "progression_delta_receipt":
            continue
        route_ref = receipt["payload"].get("route_ref") or receipt["session_ref"]
        grouped[route_ref].append(receipt)

    routes: list[dict[str, Any]] = []
    for route_ref in sorted(grouped):
        group = grouped[route_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        cumulative = axis_template()
        caution_count = 0
        for receipt in group:
            payload = receipt["payload"]
            axis_deltas = payload.get("axis_deltas", {})
            if isinstance(axis_deltas, dict):
                for axis in AXES:
                    value = axis_deltas.get(axis, 0)
                    if isinstance(value, int):
                        cumulative[axis] += value
            cautions = payload.get("cautions", [])
            if isinstance(cautions, list):
                caution_count += len(cautions)
        routes.append(
            {
                "route_ref": route_ref,
                "total_progression_receipts": len(group),
                "latest_verdict": latest["payload"].get("verdict", "unknown"),
                "latest_observed_at": latest["observed_at"],
                "cumulative_axis_deltas": cumulative,
                "caution_count": caution_count,
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
            }
        )

    return {
        "schema_version": "aoa_stats_route_progression_summary_v1",
        "generated_from": source,
        "routes": routes,
    }


def build_fork_calibration_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "decision_fork_receipt":
            continue
        route_ref = receipt["payload"].get("route_ref") or receipt["session_ref"]
        grouped[route_ref].append(receipt)

    routes: list[dict[str, Any]] = []
    for route_ref in sorted(grouped):
        group = grouped[route_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        branch_counts: Counter[str] = Counter()
        max_options = 0
        realized_outcome_link_count = 0
        for receipt in group:
            payload = receipt["payload"]
            branch = payload.get("chosen_branch") or "unrecorded"
            branch_counts[str(branch)] += 1
            option_count = fork_option_count(payload)
            if option_count > max_options:
                max_options = option_count
            realized_refs = payload.get("realized_outcome_refs", [])
            if isinstance(realized_refs, list):
                realized_outcome_link_count += len(realized_refs)
        routes.append(
            {
                "route_ref": route_ref,
                "decision_count": len(group),
                "chosen_branch_counts": dict(sorted(branch_counts.items())),
                "max_option_count": max_options,
                "realized_outcome_link_count": realized_outcome_link_count,
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "latest_observed_at": latest["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_fork_calibration_summary_v1",
        "generated_from": source,
        "routes": routes,
    }


def build_session_growth_branch_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    recommended_next_skill_counts: Counter[str] = Counter()
    owner_target_counts: Counter[str] = Counter()
    status_posture_counts: Counter[str] = Counter()
    reason_code_aggregates: Counter[str] = Counter()
    defer_count = 0

    for receipt in receipts:
        if receipt["event_kind"] != "decision_fork_receipt":
            continue
        payload = receipt["payload"]
        recommended_next_skill = followthrough_recommended_next_skill(payload)
        if is_nonempty_string(recommended_next_skill):
            recommended_next_skill_counts[recommended_next_skill] += 1
        owner_target = payload.get("owner_hypothesis") or payload.get("owner_target")
        if is_nonempty_string(owner_target):
            owner_target_counts[str(owner_target)] += 1
        status_posture = payload.get("status_posture")
        if is_nonempty_string(status_posture):
            status_posture_counts[str(status_posture)] += 1
        for reason_code in normalized_code_list(payload.get("reason_codes")):
            reason_code_aggregates[reason_code] += 1
        if payload.get("defer_allowed") is True or payload.get("defer_recommended") is True:
            defer_count += 1

    return {
        "schema_version": "aoa_stats_session_growth_branch_summary_v1",
        "generated_from": source,
        "window_ref": summary_window_ref(receipts),
        "counts_by_recommended_next_skill": string_count_map(recommended_next_skill_counts),
        "defer_count": defer_count,
        "counts_by_owner_target": string_count_map(owner_target_counts),
        "counts_by_status_posture": string_count_map(status_posture_counts),
        "reason_code_aggregates": string_count_map(reason_code_aggregates),
    }


def build_automation_pipeline_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "automation_candidate_receipt":
            continue
        pipeline_ref = automation_pipeline_ref(receipt)
        grouped[pipeline_ref].append(receipt)

    pipelines: list[dict[str, Any]] = []
    for pipeline_ref in sorted(grouped):
        group = grouped[pipeline_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        next_artifact_hints: set[str] = set()
        seed_ready_count = 0
        checkpoint_required_count = 0
        deterministic_ready_count = 0
        reversible_ready_count = 0
        for receipt in group:
            payload = receipt["payload"]
            if payload.get("seed_ready") is True:
                seed_ready_count += 1
            if payload.get("checkpoint_required") is True:
                checkpoint_required_count += 1
            if payload.get("deterministic_ready") is True:
                deterministic_ready_count += 1
            if payload.get("reversible_ready") is True:
                reversible_ready_count += 1
            next_hint = payload.get("next_artifact_hint")
            if isinstance(next_hint, str) and next_hint:
                next_artifact_hints.add(next_hint)
        pipelines.append(
            {
                "pipeline_ref": pipeline_ref,
                "candidate_count": len(group),
                "seed_ready_count": seed_ready_count,
                "checkpoint_required_count": checkpoint_required_count,
                "deterministic_ready_count": deterministic_ready_count,
                "reversible_ready_count": reversible_ready_count,
                "next_artifact_hints": sorted(next_artifact_hints),
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "latest_observed_at": latest["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_automation_pipeline_summary_v1",
        "generated_from": source,
        "pipelines": pipelines,
    }


def build_automation_followthrough_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    automation_candidate_count = 0
    seed_ready_count = 0
    not_now_count = 0
    checkpoint_required_count = 0
    playbook_seed_candidate_count = 0
    real_run_reviewed_count = 0
    blocker_aggregates: Counter[str] = Counter()

    for receipt in receipts:
        if receipt["event_kind"] != "automation_candidate_receipt":
            continue
        payload = receipt["payload"]
        automation_candidate_count += 1
        if payload.get("seed_ready") is True:
            seed_ready_count += 1
        else:
            not_now_count += 1
        if payload.get("checkpoint_required") is True:
            checkpoint_required_count += 1
        if is_nonempty_string(payload.get("playbook_seed_candidate")):
            playbook_seed_candidate_count += 1
        if payload.get("real_run_reviewed") is True:
            real_run_reviewed_count += 1
        for blocker_code in automation_blocker_codes(payload):
            blocker_aggregates[blocker_code] += 1

    return {
        "schema_version": "aoa_stats_automation_followthrough_summary_v1",
        "generated_from": source,
        "window_ref": summary_window_ref(receipts),
        "automation_candidate_count": automation_candidate_count,
        "seed_ready_count": seed_ready_count,
        "not_now_count": not_now_count,
        "checkpoint_required_count": checkpoint_required_count,
        "playbook_seed_candidate_count": playbook_seed_candidate_count,
        "real_run_reviewed_count": real_run_reviewed_count,
        "defer_count": not_now_count,
        "blocker_aggregates": string_count_map(blocker_aggregates),
    }


def build_codex_plane_deployment_summary() -> dict[str, Any]:
    source, trust, status, receipt = codex_plane_generated_from()
    trust_posture = str(trust.get("trust_posture") or "unknown")
    trust_posture_counts = {posture: 0 for posture in TRUST_POSTURES}
    if trust_posture in trust_posture_counts:
        trust_posture_counts[trust_posture] = 1

    stable_mcp_name_set = sorted(
        {
            str(name)
            for name in status.get("active_mcp_servers", [])
            if isinstance(name, str) and name
        }
    )
    drift_count = 1 if status.get("drift_detected") is True or receipt.get("deployment_state") == "drifted" else 0
    rollback_recommended_count = 1 if (
        trust_posture == "rollback_recommended"
        or receipt.get("deployment_state") == "rollback_recommended"
        or status.get("next_action") == "rollback"
    ) else 0

    return {
        "schema_version": "aoa_stats_codex_plane_deployment_summary_v1",
        "generated_from": source,
        "workspaces_total": 1,
        "latest_rollout_state": receipt.get("deployment_state") or "render_only",
        "trust_posture_counts": trust_posture_counts,
        "drift_count": drift_count,
        "rollback_recommended_count": rollback_recommended_count,
        "stable_mcp_name_set": stable_mcp_name_set,
        "latest_receipt_ref": receipt.get("rollout_receipt_id") or "",
    }


def build_codex_rollout_operations_summary() -> dict[str, Any]:
    source, deploy_history, _, _, latest = codex_trusted_rollout_generated_from()
    counts_by_state = Counter(
        str(row.get("state"))
        for row in deploy_history
        if isinstance(row.get("state"), str) and row.get("state")
    )
    return {
        "schema_version": "aoa_stats_codex_rollout_operations_summary_v1",
        "generated_from": source,
        "latest_rollout_campaign_ref": latest.get("latest_rollout_campaign_ref") or "",
        "latest_state": latest.get("latest_state") or "unknown",
        "active_drift_window_ref": latest.get("active_drift_window_ref"),
        "active_rollback_window_ref": latest.get("active_rollback_window_ref"),
        "latest_stable_rollout_campaign_ref": latest.get("latest_stable_rollout_campaign_ref") or "",
        "counts_by_state": dict(sorted(counts_by_state.items())),
        "source_refs": list(normalize_string_list(latest.get("source_refs"))),
    }


def build_codex_rollout_drift_summary() -> dict[str, Any]:
    source, deploy_history, _, _, latest = codex_trusted_rollout_generated_from()
    latest_history = deploy_history[-1]
    drift_refs = normalize_string_list(latest_history.get("drift_window_refs"))
    rollback_refs = normalize_string_list(latest_history.get("rollback_window_refs"))
    latest_state = str(latest.get("latest_state") or latest_history.get("state") or "unknown")
    return {
        "schema_version": "aoa_stats_codex_rollout_drift_summary_v1",
        "generated_from": source,
        "latest_rollout_campaign_ref": latest.get("latest_rollout_campaign_ref") or "",
        "drift_window_ref": drift_refs[0] if drift_refs else None,
        "drift_state": str(latest_history.get("drift_state") or "quiet"),
        "repair_attempted": bool(latest_history.get("repair_attempted")),
        "rollback_required": bool(rollback_refs) or latest_state in {"rollback_open", "rolled_back"},
        "source_refs": [
            "8Dionysus/generated/codex/rollout/deploy_history.jsonl",
            "8Dionysus/generated/codex/rollout/rollback_windows.min.json",
        ],
    }


def build_rollout_campaign_summary() -> dict[str, Any]:
    source, campaign, review, rollback = codex_rollout_campaign_generated_from()
    lineage_refs = campaign.get("lineage_refs")
    if not isinstance(lineage_refs, dict):
        lineage_refs = {}
    review_status = str(review.get("status") or "closed")
    rollback_status = str(rollback.get("status") or "retired")
    return {
        "schema_version": "aoa_stats_rollout_campaign_summary_v1",
        "generated_from": source,
        "campaign_ref": str(campaign.get("campaign_ref") or ""),
        "campaign_state": str(campaign.get("state") or "review_required"),
        "open_batches": 1 if campaign.get("state") == "open" else 0,
        "pending_reviews": 1 if review_status in {"review_required", "reanchor", "rollback_considered"} else 0,
        "rollback_ready_windows": 1 if rollback_status in {"ready_if_needed", "armed"} else 0,
        "stage_counts": {
            "candidate_refs": len(normalize_string_list(lineage_refs.get("candidate_refs"))),
            "seed_refs": len(normalize_string_list(lineage_refs.get("seed_refs"))),
            "object_refs": len(normalize_string_list(lineage_refs.get("object_refs"))),
        },
        "source_refs": list(source["receipt_input_paths"]),
    }


def build_drift_review_summary() -> dict[str, Any]:
    source, campaign, review, rollback = codex_rollout_campaign_generated_from()
    signals = review.get("signals")
    signal_counts: Counter[str] = Counter()
    if isinstance(signals, dict):
        for name in sorted(signals):
            signal_counts[name] = 1 if signals.get(name) is True else 0
    decision = str(review.get("decision") or "safe_stop")
    rollback_status = str(rollback.get("status") or "retired")
    return {
        "schema_version": "aoa_stats_drift_review_summary_v1",
        "generated_from": source,
        "campaign_ref": str(campaign.get("campaign_ref") or ""),
        "review_ref": str(review.get("review_ref") or ""),
        "review_status": str(review.get("status") or "closed"),
        "review_windows_total": 1,
        "signals_seen": dict(sorted(signal_counts.items())),
        "decision_counts": {decision: 1},
        "rollback_ref": str(rollback.get("rollback_ref") or ""),
        "rollback_ready": rollback_status in {"ready_if_needed", "armed"},
        "source_refs": list(source["receipt_input_paths"]),
    }


def build_continuity_window_summary() -> dict[str, Any]:
    source, continuity_window, memo_thread = continuity_window_generated_from()
    current_status = str(continuity_window.get("continuity_status") or "closed")
    successful_reanchors, failed_reanchors = continuity_reanchor_counts(
        memo_thread, current_status
    )
    revision_window_ref = continuity_window.get("revision_window_ref")
    open_revision_windows = (
        1 if current_status != "closed" and is_nonempty_string(revision_window_ref) else 0
    )
    bounded_revision_count = 1 if is_nonempty_string(revision_window_ref) else 0
    return {
        "schema_version": "aoa_stats_continuity_window_summary_v1",
        "generated_from": source,
        "continuity_ref": str(continuity_window.get("continuity_ref") or ""),
        "current_status": current_status,
        "open_revision_windows": open_revision_windows,
        "successful_reanchors": successful_reanchors,
        "failed_reanchors": failed_reanchors,
        "last_anchor_artifact_ref": str(continuity_window.get("anchor_artifact_ref") or ""),
        "drift_flags": continuity_drift_flags(current_status, failed_reanchors),
        "bounded_revision_count": bounded_revision_count,
    }


def build_runtime_closeout_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "runtime_wave_closeout_receipt":
            continue
        grouped[runtime_closeout_identity(receipt)].append(receipt)

    closeouts: list[dict[str, Any]] = []
    for key in sorted(grouped):
        program_id, wave_id = key
        group = grouped[key]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        gate_counts: Counter[str] = Counter()
        handoff_counts: Counter[str] = Counter()
        for receipt in group:
            payload = receipt["payload"]
            gate_counts[str(payload.get("gate_result") or "unknown")] += 1
            handoff_counts[
                str(payload.get("reviewed_closeout_handoff_status") or "unknown")
            ] += 1
        latest_payload = latest["payload"]
        latest_truth_status = latest_payload.get("truth_status", {})
        if not isinstance(latest_truth_status, dict):
            latest_truth_status = {}
        closeouts.append(
            {
                "program_id": program_id,
                "wave_id": wave_id,
                "closeout_receipt_count": len(group),
                "latest_gate_result": str(latest_payload.get("gate_result") or "unknown"),
                "gate_result_counts": dict(sorted(gate_counts.items())),
                "latest_reviewed_closeout_handoff_status": str(
                    latest_payload.get("reviewed_closeout_handoff_status") or "unknown"
                ),
                "reviewed_closeout_handoff_status_counts": dict(
                    sorted(handoff_counts.items())
                ),
                "latest_reviewed_closeout_audit_only": bool(
                    latest_payload.get("reviewed_closeout_audit_only")
                ),
                "latest_case_count": int(latest_payload.get("case_count") or 0),
                "latest_next_action": str(latest_payload.get("next_action") or "unspecified"),
                "latest_truth_status": {
                    "source_authored": bool(latest_truth_status.get("source_authored")),
                    "deployed": bool(latest_truth_status.get("deployed")),
                    "trial_proven": bool(latest_truth_status.get("trial_proven")),
                    "live_available": bool(latest_truth_status.get("live_available")),
                },
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": latest["observed_at"],
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
            }
        )

    return {
        "schema_version": "aoa_stats_runtime_closeout_summary_v1",
        "generated_from": source,
        "closeouts": closeouts,
    }


def build_surface_detection_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "core_skill_application_receipt":
            continue
        if receipt["payload"].get("application_stage") != "finish":
            continue
        grouped[receipt["observed_at"][:10]].append(receipt)

    windows: list[dict[str, Any]] = []
    for window_date in sorted(grouped):
        group = grouped[window_date]
        activation_counts: Counter[str] = Counter()
        adjacent_owner_repo_counts: Counter[str] = Counter()
        handoff_target_counts: Counter[str] = Counter()
        candidate_now_count = 0
        candidate_later_count = 0
        owner_layer_ambiguity_count = 0
        repeated_pattern_signal_count = 0
        promotion_discussion_count = 0
        family_entry_ref_count = 0

        for receipt in group:
            context = surface_detection_context(receipt)
            activation_truth = context.get("activation_truth")
            if isinstance(activation_truth, str) and activation_truth == "manual-equivalent-adjacent":
                activation_counts["manual-equivalent-adjacent"] += 1
            else:
                activation_counts["activated"] += 1

            candidate_counts = context.get("candidate_counts")
            if isinstance(candidate_counts, dict):
                candidate_now_count += int(candidate_counts.get("candidate_now") or 0)
                candidate_later_count += int(candidate_counts.get("candidate_later") or 0)

            if bool(context.get("owner_layer_ambiguity")):
                owner_layer_ambiguity_count += 1

            adjacent_owner_repos = context.get("adjacent_owner_repos")
            if isinstance(adjacent_owner_repos, list):
                for repo in adjacent_owner_repos:
                    if isinstance(repo, str) and repo:
                        adjacent_owner_repo_counts[repo] += 1

            handoff_targets = context.get("suggested_handoff_targets")
            if isinstance(handoff_targets, list):
                for target in handoff_targets:
                    if isinstance(target, str) and target:
                        handoff_target_counts[target] += 1

            if bool(context.get("repeated_pattern_signal")):
                repeated_pattern_signal_count += 1
            if bool(context.get("promotion_discussion_required")):
                promotion_discussion_count += 1

            family_entry_refs = context.get("family_entry_refs")
            if isinstance(family_entry_refs, list):
                family_entry_ref_count += len(
                    [ref for ref in family_entry_refs if isinstance(ref, str) and ref]
                )

        windows.append(
            {
                "window_id": f"window:{window_date}",
                "window_date": window_date,
                "core_skill_receipt_count": len(group),
                "activated_count": activation_counts["activated"],
                "manual_equivalent_adjacent_count": activation_counts["manual-equivalent-adjacent"],
                "candidate_now_count": candidate_now_count,
                "candidate_later_count": candidate_later_count,
                "owner_layer_ambiguity_count": owner_layer_ambiguity_count,
                "adjacent_owner_repo_counts": dict(sorted(adjacent_owner_repo_counts.items())),
                "handoff_target_counts": dict(sorted(handoff_target_counts.items())),
                "repeated_pattern_signal_count": repeated_pattern_signal_count,
                "promotion_discussion_count": promotion_discussion_count,
                "family_entry_ref_count": family_entry_ref_count,
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": group[-1]["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_surface_detection_summary_v1",
        "generated_from": source,
        "windows": windows,
    }


def build_summary_surface_catalog(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "aoa_stats_summary_surface_catalog_v2",
        "schema_ref": "schemas/summary-surface-catalog.schema.json",
        "owner_repo": "aoa-stats",
        "surface_kind": "runtime_surface",
        "authority_ref": "docs/ARCHITECTURE.md",
        "generated_from": source,
        "validation_refs": [
            "scripts/build_views.py",
            "scripts/validate_repo.py",
            "tests/test_summary_surface_catalog.py",
        ],
        "surfaces": [
            {
                "name": "core_skill_application_summary",
                "surface_ref": "generated/core_skill_application_summary.min.json",
                "schema_ref": "schemas/core-skill-application-summary.schema.json",
                "primary_question": "Which project-core kernel skills are actually finishing and how often, without inferring usage from general receipt volume?",
                "derivation_rule": "aggregate core_skill_application_receipt payloads by kernel_id and skill_name",
            },
            {
                "name": "object_summary",
                "surface_ref": "generated/object_summary.min.json",
                "schema_ref": "schemas/object-summary.schema.json",
                "primary_question": "How often and how broadly is each source object showing up in the current receipt feed?",
                "derivation_rule": "group receipts by object_ref and keep counts, latest timestamps, and bounded posture flags",
            },
            {
                "name": "candidate_lineage_summary",
                "surface_ref": "generated/candidate_lineage_summary.min.json",
                "schema_ref": "schemas/candidate_lineage_summary.schema.json",
                "primary_question": "How far are reviewed growth-refinery candidates actually moving without turning stats into routing or proof authority?",
                "derivation_rule": "aggregate reviewed-only candidate_lineage_entries carried on harvest_packet_receipt payloads into stage, owner-target, posture, misroute, supersession, and time-to-stage summaries",
            },
            {
                "name": "owner_landing_summary",
                "surface_ref": "generated/owner_landing_summary.min.json",
                "schema_ref": "schemas/owner-landing-summary.schema.json",
                "primary_question": "Which reviewed candidates have landed in owner-local status surfaces and how far has that landing stabilized without turning stats into owner truth?",
                "derivation_rule": "aggregate reviewed_owner_landing_receipt payloads together with seed_owner_landing_trace_receipt payloads into owner-repo, posture, outcome, and time-to-outcome summaries",
            },
            {
                "name": "supersession_drop_summary",
                "surface_ref": "generated/supersession_drop_summary.min.json",
                "schema_ref": "schemas/supersession-drop-summary.schema.json",
                "primary_question": "What pruning, replacement, merge, and reanchor signals are explicit across reviewed growth-refinery receipts without inventing reasons or ranking authority?",
                "derivation_rule": "aggregate reviewed candidate-lineage entries, reviewed_owner_landing_receipt payloads, and seed_owner_landing_trace_receipt payloads into explicit turnover summaries",
            },
            {
                "name": "repeated_window_summary",
                "surface_ref": "generated/repeated_window_summary.min.json",
                "schema_ref": "schemas/repeated-window-summary.schema.json",
                "primary_question": "What changed across bounded date windows without turning the result into one global score?",
                "derivation_rule": "group receipts by observed_at date and keep counts plus bounded window signals",
            },
            {
                "name": "route_progression_summary",
                "surface_ref": "generated/route_progression_summary.min.json",
                "schema_ref": "schemas/route-progression-summary.schema.json",
                "primary_question": "What bounded multi-axis movement is visible on each named route?",
                "derivation_rule": "aggregate progression_delta_receipt payloads by route_ref and sum axis deltas",
            },
            {
                "name": "fork_calibration_summary",
                "surface_ref": "generated/fork_calibration_summary.min.json",
                "schema_ref": "schemas/fork-calibration-summary.schema.json",
                "primary_question": "How are route forks actually being chosen and how often do they carry realized outcome refs?",
                "derivation_rule": "aggregate decision_fork_receipt payloads by route_ref and chosen_branch",
            },
            {
                "name": "session_growth_branch_summary",
                "surface_ref": "generated/session_growth_branch_summary.min.json",
                "schema_ref": "schemas/session-growth-branch-summary.schema.json",
                "primary_question": "What reviewed next-kernel branches are being recommended after closeout without turning stats into route authority?",
                "derivation_rule": "aggregate reviewed followthrough hints carried on decision_fork_receipt payloads into next-skill, owner-target, posture, defer, and reason-code counts",
            },
            {
                "name": "automation_pipeline_summary",
                "surface_ref": "generated/automation_pipeline_summary.min.json",
                "schema_ref": "schemas/automation-pipeline-summary.schema.json",
                "primary_question": "How close is a named automation pipeline to seed-ready bounded use?",
                "derivation_rule": "aggregate automation_candidate_receipt payloads by pipeline_ref and readiness flags",
            },
            {
                "name": "automation_followthrough_summary",
                "surface_ref": "generated/automation_followthrough_summary.min.json",
                "schema_ref": "schemas/automation-followthrough-summary.schema.json",
                "primary_question": "How far are reviewed automation candidates moving through bounded follow-through without implying scheduler authority?",
                "derivation_rule": "aggregate automation_candidate_receipt payloads into seed-ready, defer, checkpoint, playbook-seed, real-run-review, and blocker counts",
            },
            {
                "name": "codex_plane_deployment_summary",
                "surface_ref": "generated/codex_plane_deployment_summary.min.json",
                "schema_ref": "schemas/codex-plane-deployment-summary.schema.json",
                "primary_question": "What is the current derived deployment continuity posture for the shared-root Codex plane without letting stats overrule live trust evidence?",
                "derivation_rule": "derive one bounded deployment summary from the 8Dionysus trust-state and rollout receipt examples plus the aoa-sdk deploy-status example",
            },
            {
                "name": "codex_rollout_operations_summary",
                "surface_ref": "generated/codex_rollout_operations_summary.min.json",
                "schema_ref": "schemas/codex-rollout-operations-summary.schema.json",
                "primary_question": "What checked-in trusted rollout campaign posture is currently visible for the shared-root Codex plane without turning stats into rollout authority?",
                "derivation_rule": "derive bounded rollout state counts and latest campaign posture from 8Dionysus checked-in generated/codex/rollout source surfaces",
            },
            {
                "name": "codex_rollout_drift_summary",
                "surface_ref": "generated/codex_rollout_drift_summary.min.json",
                "schema_ref": "schemas/codex-rollout-drift-summary.schema.json",
                "primary_question": "What is the current bounded drift and rollback posture of the latest trusted Codex rollout campaign without replacing source-owned campaign history?",
                "derivation_rule": "derive the latest drift window, drift state, repair attempt posture, and rollback requirement from 8Dionysus checked-in rollout history and rollback windows",
            },
            {
                "name": "rollout_campaign_summary",
                "surface_ref": "generated/rollout_campaign_summary.min.json",
                "schema_ref": "schemas/rollout-campaign-summary.schema.json",
                "primary_question": "What is the current bounded campaign cadence posture for the shared-root Codex plane without turning stats into cadence authority?",
                "derivation_rule": "derive one current campaign-cadence summary from 8Dionysus source-owned rollout campaign, drift-review, and rollback-followthrough window examples",
            },
            {
                "name": "drift_review_summary",
                "surface_ref": "generated/drift_review_summary.min.json",
                "schema_ref": "schemas/drift-review-summary.schema.json",
                "primary_question": "What named drift signals and explicit review decisions are currently visible in the source-owned cadence windows without replacing rollout or campaign truth?",
                "derivation_rule": "derive one bounded drift-review summary from the current 8Dionysus cadence windows and keep rollback readiness descriptive only",
            },
            {
                "name": "continuity_window_summary",
                "surface_ref": "generated/continuity_window_summary.min.json",
                "schema_ref": "schemas/continuity-window-summary.schema.json",
                "primary_question": "What is the current bounded self-agency continuity posture without turning stats into continuity truth or self-agency proof?",
                "derivation_rule": "derive one bounded continuity snapshot from the aoa-agents continuity window example, the sovereign continuity playbook, the memo-side provenance thread example, and the landed continuity eval anchors",
            },
            {
                "name": "runtime_closeout_summary",
                "surface_ref": "generated/runtime_closeout_summary.min.json",
                "schema_ref": "schemas/runtime-closeout-summary.schema.json",
                "primary_question": "What is the current bounded runtime closeout posture across program waves and how did reviewed handoff land?",
                "derivation_rule": "aggregate runtime_wave_closeout_receipt payloads by program_id and wave_id and keep the latest gate plus handoff posture",
            },
            {
                "name": "stress_recovery_window_summary",
                "surface_ref": "generated/stress_recovery_window_summary.min.json",
                "schema_ref": "schemas/stress-recovery-window-summary.schema.json",
                "primary_question": "What does the current repeated-window stress recovery proof family say without inventing a new canonical event kind or outranking owner evidence?",
                "derivation_rule": "resolve aoa-stress-recovery-window eval_result_receipt report_ref paths through aoa-evals and derive one bounded summary plus suppression posture",
            },
            {
                "name": "surface_detection_summary",
                "surface_ref": "generated/surface_detection_summary.min.json",
                "schema_ref": "schemas/surface-detection-summary.schema.json",
                "primary_question": "What second-wave surface-detection signals are accumulating without turning stats into routing authority?",
                "derivation_rule": "aggregate advisory surface_detection_context payloads on finish-stage core_skill_application_receipt envelopes by observed date",
            },
        ],
    }


def build_all_views(
    receipts: list[dict[str, Any]], input_paths: list[str], *, evals_root: Path | None = None
) -> dict[str, dict[str, Any]]:
    active_receipts = resolve_active_receipts(receipts)
    source = generated_from(active_receipts, input_paths)
    resolved_evals_root = (
        evals_root.expanduser().resolve() if evals_root is not None else DEFAULT_EVALS_ROOT.resolve()
    )
    return {
        "object_summary.min.json": build_object_summary(active_receipts, source),
        "candidate_lineage_summary.min.json": build_candidate_lineage_summary(
            active_receipts, source
        ),
        "owner_landing_summary.min.json": build_owner_landing_summary(active_receipts, source),
        "supersession_drop_summary.min.json": build_supersession_drop_summary(
            active_receipts, source
        ),
        "core_skill_application_summary.min.json": build_core_skill_application_summary(
            active_receipts, source
        ),
        "repeated_window_summary.min.json": build_repeated_window_summary(active_receipts, source),
        "route_progression_summary.min.json": build_route_progression_summary(active_receipts, source),
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
        "codex_plane_deployment_summary.min.json": build_codex_plane_deployment_summary(),
        "codex_rollout_operations_summary.min.json": build_codex_rollout_operations_summary(),
        "codex_rollout_drift_summary.min.json": build_codex_rollout_drift_summary(),
        "rollout_campaign_summary.min.json": build_rollout_campaign_summary(),
        "drift_review_summary.min.json": build_drift_review_summary(),
        "continuity_window_summary.min.json": build_continuity_window_summary(),
        "runtime_closeout_summary.min.json": build_runtime_closeout_summary(active_receipts, source),
        "stress_recovery_window_summary.min.json": build_stress_recovery_window_summary(
            active_receipts, source, evals_root=resolved_evals_root
        ),
        "surface_detection_summary.min.json": build_surface_detection_summary(active_receipts, source),
        "summary_surface_catalog.min.json": build_summary_surface_catalog(source),
    }


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
        [path.name for path in input_paths],
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
