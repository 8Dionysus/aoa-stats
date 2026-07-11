from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .codex_plane_deployment import validate_codex_plane_deployment_chain
from .receipt_abi import ReceiptValidationError


CODEX_PLANE_TRUST_STATE_EXAMPLE = Path(
    "examples/codex_plane_trust_state.example.json"
)
CODEX_PLANE_REGENERATION_REPORT_EXAMPLE = Path(
    "examples/codex_plane_regeneration_report.example.json"
)
CODEX_PLANE_ROLLOUT_RECEIPT_EXAMPLE = Path(
    "examples/codex_plane_rollout_receipt.example.json"
)
CODEX_PLANE_LIVE_ROLLOUT_ROOT = Path(".codex/generated/rollout")
CODEX_PLANE_LIVE_TRUST_STATE = (
    CODEX_PLANE_LIVE_ROLLOUT_ROOT / "codex_plane_trust_state.current.json"
)
CODEX_PLANE_LIVE_REGENERATION_REPORT = (
    CODEX_PLANE_LIVE_ROLLOUT_ROOT
    / "codex_plane_regeneration_report.latest.json"
)
CODEX_PLANE_LIVE_ROLLOUT_RECEIPT = (
    CODEX_PLANE_LIVE_ROLLOUT_ROOT / "codex_plane_rollout_receipt.latest.json"
)


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
class CodexPlaneDeploymentInputBundle:
    source: Mapping[str, Any]
    trust: Mapping[str, Any]
    regeneration: Mapping[str, Any]
    receipt: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", _freeze(self.source))
        object.__setattr__(self, "trust", _freeze(self.trust))
        object.__setattr__(self, "regeneration", _freeze(self.regeneration))
        object.__setattr__(self, "receipt", _freeze(self.receipt))

    def mutable_parts(
        self,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Preserve the historical root tuple contract for compatibility."""

        return (
            _thaw(self.source),
            _thaw(self.trust),
            _thaw(self.regeneration),
            _thaw(self.receipt),
        )


def codex_plane_reference_paths(owner_root: Path) -> tuple[Path, Path, Path]:
    return (
        owner_root / CODEX_PLANE_TRUST_STATE_EXAMPLE,
        owner_root / CODEX_PLANE_REGENERATION_REPORT_EXAMPLE,
        owner_root / CODEX_PLANE_ROLLOUT_RECEIPT_EXAMPLE,
    )


def codex_plane_live_paths(workspace_root: Path) -> tuple[Path, Path, Path]:
    return (
        workspace_root / CODEX_PLANE_LIVE_TRUST_STATE,
        workspace_root / CODEX_PLANE_LIVE_REGENERATION_REPORT,
        workspace_root / CODEX_PLANE_LIVE_ROLLOUT_RECEIPT,
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


def _build_bundle(
    *,
    paths: tuple[Path, Path, Path],
    source_refs: tuple[str, str, str],
) -> CodexPlaneDeploymentInputBundle:
    trust_path, regeneration_path, receipt_path = paths
    trust = _load_json_object(trust_path, label="Codex Plane trust state")
    regeneration = _load_json_object(
        regeneration_path, label="Codex Plane regeneration report"
    )
    receipt = _load_json_object(receipt_path, label="Codex Plane rollout receipt")
    latest_observed_at = validate_codex_plane_deployment_chain(
        trust, regeneration, receipt
    )
    return CodexPlaneDeploymentInputBundle(
        source={
            "receipt_input_paths": list(source_refs),
            "total_receipts": 1,
            "latest_observed_at": latest_observed_at.isoformat().replace(
                "+00:00", "Z"
            ),
        },
        trust=trust,
        regeneration=regeneration,
        receipt=receipt,
    )


def load_codex_plane_reference_bundle(
    owner_root: Path,
) -> CodexPlaneDeploymentInputBundle:
    owner_root = owner_root.expanduser().resolve()
    paths = codex_plane_reference_paths(owner_root)
    refs = tuple(
        f"8Dionysus/{path.relative_to(owner_root).as_posix()}" for path in paths
    )
    return _build_bundle(paths=paths, source_refs=refs)


def load_codex_plane_live_bundle(
    workspace_root: Path,
) -> CodexPlaneDeploymentInputBundle | None:
    workspace_root = workspace_root.expanduser().resolve()
    paths = codex_plane_live_paths(workspace_root)
    if not any(path.is_file() for path in paths):
        return None
    refs = tuple(
        f"workspace-root/{path.relative_to(workspace_root).as_posix()}"
        for path in paths
    )
    bundle = _build_bundle(paths=paths, source_refs=refs)
    declared_workspace_root = Path(str(bundle.trust["workspace_root"])).expanduser()
    if (
        not declared_workspace_root.is_absolute()
        or declared_workspace_root.resolve() != workspace_root
    ):
        raise ReceiptValidationError(
            "Codex Plane live trust-state workspace_root must match the selected "
            f"workspace root: expected {workspace_root}, got "
            f"{bundle.trust['workspace_root']!r}"
        )
    return bundle
