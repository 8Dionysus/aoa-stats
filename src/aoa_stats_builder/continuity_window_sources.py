from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .continuity_window import validate_continuity_window_reference_chain
from .receipt_abi import ReceiptValidationError


AGENTS_CONTINUITY_WINDOW_EXAMPLE = Path(
    "mechanics/checkpoint/parts/continuity-lane/examples/"
    "self-agency-continuity-window.example.json"
)
PLAYBOOK_CONTINUITY_CYCLE = Path(
    "playbooks/continuity/session-growth/self-agency-continuity-cycle/PLAYBOOK.md"
)
MEMO_CONTINUITY_PROVENANCE_THREAD = Path(
    "mechanics/writeback/parts/growth-and-continuity/examples/"
    "provenance_thread.self-agency-continuity.example.json"
)
MEMO_CONTINUITY_PROVENANCE_THREAD_FALLBACKS = (
    Path(
        "mechanics/writeback/examples/"
        "provenance_thread.self-agency-continuity.example.json"
    ),
)
EVAL_CATALOG = Path("generated/eval_catalog.min.json")


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class ContinuityWindowInputBundle:
    source: Mapping[str, Any]
    continuity_window: Mapping[str, Any]
    memo_thread: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", _freeze(self.source))
        object.__setattr__(self, "continuity_window", _freeze(self.continuity_window))
        object.__setattr__(self, "memo_thread", _freeze(self.memo_thread))

    def mutable_parts(
        self,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Preserve the historical root tuple contract for compatibility callers."""

        return (
            _thaw(self.source),
            _thaw(self.continuity_window),
            _thaw(self.memo_thread),
        )


def continuity_window_reference_paths(
    *,
    agents_root: Path,
    playbooks_root: Path,
    memo_root: Path,
    evals_root: Path,
) -> tuple[Path, Path, Path, Path]:
    return (
        agents_root / AGENTS_CONTINUITY_WINDOW_EXAMPLE,
        playbooks_root / PLAYBOOK_CONTINUITY_CYCLE,
        memo_root / MEMO_CONTINUITY_PROVENANCE_THREAD,
        evals_root / EVAL_CATALOG,
    )


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReceiptValidationError(f"invalid JSON in {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise ReceiptValidationError(f"{label} must be a JSON object: {path}")
    return payload


def _load_text(path: Path, *, label: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc
    if not text.strip():
        raise ReceiptValidationError(f"{label} must not be empty: {path}")
    return text


def _resolved_memo_path(memo_root: Path, primary_path: Path) -> Path:
    for candidate in (
        primary_path,
        *(memo_root / relative for relative in MEMO_CONTINUITY_PROVENANCE_THREAD_FALLBACKS),
    ):
        if candidate.is_file():
            return candidate
    return primary_path


def _frontmatter_scalar(value: str) -> str:
    normalized = value.strip()
    if (
        len(normalized) >= 2
        and normalized[0] == normalized[-1]
        and normalized[0] in {'"', "'"}
    ):
        return normalized[1:-1]
    return normalized


def parse_playbook_frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ReceiptValidationError(
            "self-agency continuity playbook must expose YAML frontmatter"
        )
    try:
        end_index = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration as exc:
        raise ReceiptValidationError(
            "self-agency continuity playbook frontmatter must be closed"
        ) from exc

    payload: dict[str, Any] = {}
    active_list_key: str | None = None
    for line_number, raw_line in enumerate(lines[1:end_index], start=2):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("  - ") and active_list_key is not None:
            item = _frontmatter_scalar(raw_line[4:])
            if not item:
                raise ReceiptValidationError(
                    "self-agency continuity playbook frontmatter "
                    f"line {line_number} has an empty list item"
                )
            payload[active_list_key].append(item)
            continue
        if raw_line[:1].isspace() or ":" not in raw_line:
            raise ReceiptValidationError(
                "self-agency continuity playbook frontmatter "
                f"line {line_number} is outside the supported flat contract"
            )
        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        if not key or key in payload:
            raise ReceiptValidationError(
                "self-agency continuity playbook frontmatter "
                f"line {line_number} has an invalid or duplicate key"
            )
        value = _frontmatter_scalar(raw_value)
        if value:
            payload[key] = value
            active_list_key = None
        else:
            payload[key] = []
            active_list_key = key
    return payload


def _display_repo_path(repo_name: str, repo_root: Path, path: Path) -> str:
    try:
        relative_path = path.relative_to(repo_root)
    except ValueError as exc:
        raise ReceiptValidationError(
            f"{repo_name} continuity source escaped its configured repo root: {path}"
        ) from exc
    return f"{repo_name}/{relative_path.as_posix()}"


def load_continuity_window_reference_bundle(
    *,
    agents_root: Path,
    playbooks_root: Path,
    memo_root: Path,
    evals_root: Path,
) -> ContinuityWindowInputBundle:
    agents_root = agents_root.expanduser().resolve()
    playbooks_root = playbooks_root.expanduser().resolve()
    memo_root = memo_root.expanduser().resolve()
    evals_root = evals_root.expanduser().resolve()
    continuity_path, playbook_path, memo_path, eval_catalog_path = (
        continuity_window_reference_paths(
            agents_root=agents_root,
            playbooks_root=playbooks_root,
            memo_root=memo_root,
            evals_root=evals_root,
        )
    )
    resolved_memo_path = _resolved_memo_path(memo_root, memo_path)

    continuity_window = _load_json_object(
        continuity_path,
        label="self-agency continuity window example",
    )
    playbook_contract = parse_playbook_frontmatter(
        _load_text(playbook_path, label="self-agency continuity playbook")
    )
    memo_thread = _load_json_object(
        resolved_memo_path,
        label="self-agency continuity provenance thread example",
    )
    eval_catalog = _load_json_object(
        eval_catalog_path,
        label="continuity eval catalog",
    )
    latest_observed_at = validate_continuity_window_reference_chain(
        continuity_window,
        memo_thread,
        playbook_contract,
        eval_catalog,
    )
    source = {
        "receipt_input_paths": [
            _display_repo_path("aoa-agents", agents_root, continuity_path),
            _display_repo_path("aoa-playbooks", playbooks_root, playbook_path),
            _display_repo_path("aoa-memo", memo_root, resolved_memo_path),
            _display_repo_path("aoa-evals", evals_root, eval_catalog_path),
        ],
        "total_receipts": 1,
        "latest_observed_at": latest_observed_at.isoformat().replace("+00:00", "Z"),
    }
    return ContinuityWindowInputBundle(
        source=source,
        continuity_window=continuity_window,
        memo_thread=memo_thread,
    )
