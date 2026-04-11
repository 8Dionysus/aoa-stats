from __future__ import annotations

import json
import logging
from typing import Any

from aoa_stats_mcp.repo_state import RepoState, build_surface_payload

LOGGER = logging.getLogger(__name__)


def build_server() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency 'mcp'. Install it with: python -m pip install -r requirements-mcp.txt"
        ) from exc

    state = RepoState.discover()
    mcp = FastMCP("aoa-stats", json_response=True)

    @mcp.tool()
    def stats_catalog() -> dict[str, Any]:
        """Return the compact aoa-stats runtime-entry catalog for generated summary surfaces."""
        return state.load_catalog()

    @mcp.tool()
    def stats_surface_read(
        surface_name: str | None = None,
        surface_ref: str | None = None,
        mode: str = "preview",
        limit: int = 5,
    ) -> dict[str, Any]:
        """Read one generated summary surface by name or ref.

        Prefer preview mode first. Use full mode only when a task truly needs the whole surface.
        """

        return build_surface_payload(
            state,
            surface_name=surface_name,
            surface_ref=surface_ref,
            mode=mode,
            limit=limit,
        )

    @mcp.tool()
    def stats_source_registry() -> dict[str, Any]:
        """Return the canonical aoa-stats live receipt source registry."""
        return state.load_source_registry()

    @mcp.tool()
    def stats_boundary_rules() -> dict[str, Any]:
        """Return the small boundary bundle that keeps aoa-stats derived-only and non-sovereign."""
        return state.build_boundary_bundle()

    @mcp.resource("aoa-stats://catalog")
    def catalog_resource() -> str:
        """Compact runtime-entry catalog for generated surfaces."""
        return json.dumps(state.load_catalog(), ensure_ascii=False, indent=2)

    @mcp.resource("aoa-stats://source-registry")
    def source_registry_resource() -> str:
        """Canonical owner-local live receipt source registry."""
        return json.dumps(state.load_source_registry(), ensure_ascii=False, indent=2)

    @mcp.resource("aoa-stats://boundaries")
    def boundaries_resource() -> str:
        """Boundary bundle for derived-only aoa-stats posture."""
        return json.dumps(state.build_boundary_bundle(), ensure_ascii=False, indent=2)

    @mcp.resource("aoa-stats://surface/{name}")
    def surface_resource(name: str) -> str:
        """One generated surface by catalog name."""
        return json.dumps(
            build_surface_payload(state, surface_name=name, mode="full", limit=5),
            ensure_ascii=False,
            indent=2,
        )

    @mcp.prompt()
    def inspect_stats_surface(name: str) -> str:
        """Prompt recipe for reading one aoa-stats surface without letting it outrank owner meaning."""
        return (
            "Use stats_boundary_rules first. Then inspect stats_catalog and "
            f"stats_surface_read(surface_name='{name}', mode='preview'). "
            "Treat aoa-stats as derived-only context. Do not turn counts or summaries into workflow "
            "authority, proof authority, or quest-state authority."
        )

    @mcp.prompt()
    def compare_stats_surfaces(left: str, right: str) -> str:
        """Prompt recipe for comparing two aoa-stats surfaces."""
        return (
            "Use stats_boundary_rules first. Then inspect stats_catalog, followed by "
            f"stats_surface_read(surface_name='{left}', mode='preview') and "
            f"stats_surface_read(surface_name='{right}', mode='preview'). "
            "Compare only what the derived surfaces actually summarize. Explicitly call out where a "
            "source repo would be needed for canonical meaning."
        )

    LOGGER.info("aoa-stats MCP server ready at repo root: %s", state.repo_root)
    return mcp


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    server = build_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
