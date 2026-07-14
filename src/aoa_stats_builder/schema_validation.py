from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


def schema_issues(
    schema: Mapping[str, Any],
    payload: Mapping[str, Any],
    *,
    label: str,
    registry: Registry[Any] | None = None,
) -> list[str]:
    """Return deterministic JSON Schema findings for one object."""

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
        registry=registry or Registry(),
    )
    issues: list[str] = []
    for error in sorted(
        validator.iter_errors(payload), key=lambda item: list(item.absolute_path)
    ):
        location = ".".join(str(part) for part in error.absolute_path)
        suffix = f":{location}" if location else ""
        issues.append(f"{label}{suffix}: {error.message}")
    return issues


def schema_registry(
    schemas: Mapping[str, Mapping[str, Any]],
) -> Registry[Any]:
    """Build a registry from schema ids without filesystem or network lookup."""

    registry: Registry[Any] = Registry()
    for schema in schemas.values():
        schema_id = schema.get("$id")
        if isinstance(schema_id, str):
            registry = registry.with_resource(
                schema_id, Resource.from_contents(schema)
            )
    return registry
