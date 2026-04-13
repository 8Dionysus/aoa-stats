from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CATALOG_RELATIVE = Path("generated/summary_surface_catalog.min.json")
LIVE_CATALOG_RELATIVE = Path("state/generated/summary_surface_catalog.min.json")
BOUNDARIES_RELATIVE = Path("docs/BOUNDARIES.md")
ARCHITECTURE_RELATIVE = Path("docs/ARCHITECTURE.md")
SOURCE_REGISTRY_RELATIVE = Path("config/live_receipt_sources.json")
REPO_SENTINELS = (
    CATALOG_RELATIVE,
    BOUNDARIES_RELATIVE,
    ARCHITECTURE_RELATIVE,
    SOURCE_REGISTRY_RELATIVE,
)


class RepoStateError(RuntimeError):
    """Raised when the aoa-stats repo state cannot be resolved safely."""


@dataclass(frozen=True)
class RepoState:
    """Thin read-only view over aoa-stats active summary surfaces and guidance files."""

    repo_root: Path

    @classmethod
    def discover(cls, start: Path | None = None) -> "RepoState":
        return cls(find_repo_root(start=start))

    def active_catalog_relative(self) -> Path:
        live_catalog = self.repo_root / LIVE_CATALOG_RELATIVE
        return LIVE_CATALOG_RELATIVE if live_catalog.is_file() else CATALOG_RELATIVE

    def load_catalog(self) -> dict[str, Any]:
        catalog_relative = self.active_catalog_relative()
        catalog = load_json_file(self.repo_root / catalog_relative)
        return normalize_catalog_surface_refs(catalog, catalog_relative=catalog_relative)

    def load_source_registry(self) -> dict[str, Any]:
        return load_json_file(self.repo_root / SOURCE_REGISTRY_RELATIVE)

    def load_boundaries_text(self) -> str:
        return load_text_file(self.repo_root / BOUNDARIES_RELATIVE)

    def load_architecture_text(self) -> str:
        return load_text_file(self.repo_root / ARCHITECTURE_RELATIVE)

    def list_surfaces(self) -> list[dict[str, Any]]:
        catalog = self.load_catalog()
        surfaces = catalog.get("surfaces")
        if not isinstance(surfaces, list):
            raise RepoStateError("summary surface catalog is missing a 'surfaces' list")
        return surfaces

    def surface_index(self) -> dict[str, dict[str, Any]]:
        index: dict[str, dict[str, Any]] = {}
        for surface in self.list_surfaces():
            name = surface.get("name")
            if isinstance(name, str):
                index[name] = surface
        return index

    def resolve_surface_path(
        self,
        *,
        surface_name: str | None = None,
        surface_ref: str | None = None,
    ) -> Path:
        if (surface_name is None and surface_ref is None) or (
            surface_name is not None and surface_ref is not None
        ):
            raise RepoStateError("provide exactly one of surface_name or surface_ref")

        if surface_name is not None:
            surface = self.surface_index().get(surface_name)
            if surface is None:
                available = ", ".join(sorted(self.surface_index()))
                raise RepoStateError(
                    f"unknown surface_name '{surface_name}'. Available surfaces: {available}"
                )
            surface_ref = surface.get("surface_ref")
            if not isinstance(surface_ref, str) or not surface_ref:
                raise RepoStateError(
                    f"catalog entry for '{surface_name}' is missing a valid surface_ref"
                )

        assert surface_ref is not None
        path = safe_repo_path(self.repo_root, surface_ref)
        if not path.is_file():
            raise RepoStateError(f"surface file does not exist: {path}")
        return path

    def load_surface(
        self,
        *,
        surface_name: str | None = None,
        surface_ref: str | None = None,
    ) -> Any:
        path = self.resolve_surface_path(surface_name=surface_name, surface_ref=surface_ref)
        return load_json_file(path)

    def build_boundary_bundle(self) -> dict[str, Any]:
        return {
            "owner_repo": "aoa-stats",
            "surface_kind": "derived_boundary_bundle",
            "boundary_ref": str(BOUNDARIES_RELATIVE),
            "architecture_ref": str(ARCHITECTURE_RELATIVE),
            "boundary_text": self.load_boundaries_text(),
            "architecture_text": self.load_architecture_text(),
        }


def find_repo_root(start: Path | None = None) -> Path:
    env_root = os.getenv("AOA_STATS_REPO_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        validate_repo_root(candidate)
        return candidate

    probe_start = (start or Path(__file__)).resolve()
    current = probe_start if probe_start.is_dir() else probe_start.parent
    for candidate in (current, *current.parents):
        try:
            validate_repo_root(candidate)
        except RepoStateError:
            continue
        return candidate
    raise RepoStateError(
        "could not find aoa-stats repo root. Set AOA_STATS_REPO_ROOT or run from inside the repo."
    )


def validate_repo_root(repo_root: Path) -> None:
    missing = [str(path) for path in REPO_SENTINELS if not (repo_root / path).exists()]
    if missing:
        raise RepoStateError(
            f"{repo_root} does not look like aoa-stats; missing required files: {', '.join(missing)}"
        )


def load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RepoStateError(f"invalid JSON in {path}") from exc


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_catalog_surface_refs(
    catalog: dict[str, Any], *, catalog_relative: Path
) -> dict[str, Any]:
    if catalog_relative != LIVE_CATALOG_RELATIVE:
        return catalog

    surfaces = catalog.get("surfaces")
    if not isinstance(surfaces, list):
        return catalog

    normalized: dict[str, Any] = dict(catalog)
    normalized["surfaces"] = [
        normalize_surface_entry(surface) if isinstance(surface, dict) else surface
        for surface in surfaces
    ]
    return normalized


def normalize_surface_entry(surface: dict[str, Any]) -> dict[str, Any]:
    surface_ref = surface.get("surface_ref")
    if not isinstance(surface_ref, str) or not surface_ref.startswith("generated/"):
        return surface

    normalized = dict(surface)
    normalized["surface_ref"] = str(Path("state") / surface_ref)
    return normalized


def safe_repo_path(repo_root: Path, relative_path: str | Path) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute():
        raise RepoStateError("absolute paths are not allowed")

    repo_root_resolved = repo_root.resolve()
    resolved = (repo_root_resolved / relative).resolve()
    try:
        resolved.relative_to(repo_root_resolved)
    except ValueError as exc:
        raise RepoStateError(f"ref escapes repo root: {relative}") from exc
    return resolved


def preview_json(value: Any, *, limit: int = 5) -> Any:
    if limit < 1:
        raise RepoStateError("preview limit must be >= 1")

    if isinstance(value, list):
        return {
            "preview_only": True,
            "total_items": len(value),
            "preview_limit": limit,
            "items": value[:limit],
        }

    if isinstance(value, dict):
        preview: dict[str, Any] = {"preview_only": True, "preview_limit": limit}
        for key, item in value.items():
            if isinstance(item, list):
                preview[key] = item[:limit]
                preview[f"{key}_total_items"] = len(item)
            else:
                preview[key] = item
        return preview

    return value


def build_surface_payload(
    state: RepoState,
    *,
    surface_name: str | None = None,
    surface_ref: str | None = None,
    mode: str = "preview",
    limit: int = 5,
) -> dict[str, Any]:
    path = state.resolve_surface_path(surface_name=surface_name, surface_ref=surface_ref)
    data = load_json_file(path)
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"preview", "full"}:
        raise RepoStateError("mode must be 'preview' or 'full'")

    payload = preview_json(data, limit=limit) if normalized_mode == "preview" else data
    return {
        "owner_repo": "aoa-stats",
        "surface_kind": "derived_summary_surface",
        "surface_ref": str(path.relative_to(state.repo_root)),
        "mode": normalized_mode,
        "payload": payload,
    }
