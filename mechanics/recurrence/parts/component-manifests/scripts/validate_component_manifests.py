#!/usr/bin/env python3
"""Validate the recurrence component/hook manifest contract."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any, Iterator


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
COMPONENTS_DIR = PART_ROOT / "manifests" / "components"
HOOKS_DIR = PART_ROOT / "manifests" / "hooks"
EXPECTED_PAIR_COUNT = 8
PATH_PREFIXES = (
    "config/",
    "docs/",
    "generated/",
    "mechanics/",
    "schemas/",
    "scripts/",
    "tests/",
)
STALE_ROOT_PREFIXES = (
    "config/agon_",
    "docs/AGON_",
    "schemas/agon-",
    "scripts/build_agon_",
    "scripts/validate_agon_",
    "tests/test_agon_",
)


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: manifest must be a JSON object")
    return payload


def iter_strings(
    value: Any, path: tuple[str, ...] = ()
) -> Iterator[tuple[tuple[str, ...], str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, (*path, str(key)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, (*path, str(index)))
    elif isinstance(value, str):
        yield path, value


def canonical_component_identity(value: str) -> str:
    normalized = value.replace(":", ".")
    if normalized.endswith(".hooks"):
        normalized = normalized[: -len(".hooks")]
    if normalized.startswith("hooks.component."):
        normalized = normalized.removeprefix("hooks.")
    elif normalized.startswith("hooks.agon."):
        normalized = "component." + normalized.removeprefix("hooks.")
    return normalized


def component_identity(payload: dict[str, Any]) -> str | None:
    for key in ("component_id", "component_ref"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return canonical_component_identity(value)
    return None


def hook_component_identity(payload: dict[str, Any]) -> str | None:
    for key in ("component_id", "component_ref", "observes_component"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return canonical_component_identity(value)
    bindings = payload.get("bindings")
    if isinstance(bindings, list):
        for binding in bindings:
            if not isinstance(binding, dict):
                continue
            value = binding.get("component_ref")
            if isinstance(value, str) and value:
                return canonical_component_identity(value)
    for key in ("hook_binding_set_id", "hook_set_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return canonical_component_identity(value)
    return None


def pair_names(components_dir: Path, hooks_dir: Path) -> tuple[set[str], set[str]]:
    components = {
        path.name.removesuffix(".json")
        for path in components_dir.glob("component.*.json")
    }
    hooks = {
        path.name.removesuffix(".hooks.json")
        for path in hooks_dir.glob("component.*.hooks.json")
    }
    return components, hooks


def validate_inventory(components_dir: Path, hooks_dir: Path) -> list[str]:
    components, hooks = pair_names(components_dir, hooks_dir)
    issues: list[str] = []
    if len(components) != EXPECTED_PAIR_COUNT:
        issues.append(
            f"component inventory must contain {EXPECTED_PAIR_COUNT} manifests, "
            f"found {len(components)}"
        )
    if len(hooks) != EXPECTED_PAIR_COUNT:
        issues.append(
            f"hook inventory must contain {EXPECTED_PAIR_COUNT} manifests, "
            f"found {len(hooks)}"
        )
    if components != hooks:
        issues.append(
            "component/hook filenames are not paired; "
            f"missing_hooks={sorted(components - hooks)!r}, "
            f"missing_components={sorted(hooks - components)!r}"
        )
    return issues


def _path_exists(repo_root: Path, route: str) -> bool:
    if any(token in route for token in ("*", "?", "[")):
        return any(repo_root.glob(route))
    return (repo_root / route).is_file()


def validate_payload_refs(
    payload: dict[str, Any], *, label: str, repo_root: Path
) -> list[str]:
    issues: list[str] = []
    for location, value in iter_strings(payload):
        route = value
        if value.startswith("python "):
            tokens = shlex.split(value)
            if len(tokens) < 2 or tokens[1] == "-m":
                continue
            route = tokens[1]
        if not route.startswith(PATH_PREFIXES):
            continue
        dotted_location = ".".join(location)
        if route.startswith(STALE_ROOT_PREFIXES):
            issues.append(
                f"{label}:{dotted_location}: stale former root route: {route}"
            )
            continue
        if not _path_exists(repo_root, route):
            issues.append(
                f"{label}:{dotted_location}: referenced route is missing: {route}"
            )
    return issues


def validate_pair_payloads(
    component: dict[str, Any],
    hook: dict[str, Any],
    *,
    expected_identity: str,
    label: str,
) -> list[str]:
    issues: list[str] = []
    component_actual = component_identity(component)
    hook_actual = hook_component_identity(hook)
    if component_actual != expected_identity:
        issues.append(
            f"{label}: component identity mismatch: expected {expected_identity!r}, "
            f"found {component_actual!r}"
        )
    if hook_actual != expected_identity:
        issues.append(
            f"{label}: hook identity mismatch: expected {expected_identity!r}, "
            f"found {hook_actual!r}"
        )
    component_wave = component.get("wave")
    hook_wave = hook.get("wave")
    if (
        component_wave is not None
        and hook_wave is not None
        and component_wave != hook_wave
    ):
        issues.append(
            f"{label}: component/hook wave mismatch: "
            f"{component_wave!r} != {hook_wave!r}"
        )
    return issues


def validate(repo_root: Path = REPO_ROOT, part_root: Path | None = None) -> list[str]:
    repo_root = repo_root.resolve()
    active_part = (part_root or PART_ROOT).resolve()
    components_dir = active_part / "manifests" / "components"
    hooks_dir = active_part / "manifests" / "hooks"
    issues = validate_inventory(components_dir, hooks_dir)
    components, hooks = pair_names(components_dir, hooks_dir)
    for name in sorted(components & hooks):
        component_path = components_dir / f"{name}.json"
        hook_path = hooks_dir / f"{name}.hooks.json"
        try:
            component = load_object(component_path)
            hook = load_object(hook_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            issues.append(str(exc))
            continue
        issues.extend(
            validate_pair_payloads(
                component,
                hook,
                expected_identity=canonical_component_identity(name),
                label=name,
            )
        )
        issues.extend(
            validate_payload_refs(
                component, label=component_path.name, repo_root=repo_root
            )
        )
        issues.extend(
            validate_payload_refs(hook, label=hook_path.name, repo_root=repo_root)
        )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--part-root", type=Path, default=PART_ROOT)
    args = parser.parse_args(argv)
    issues = validate(args.repo_root, args.part_root)
    if issues:
        print("Component manifest validation failed.")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(
        f"[ok] validated {EXPECTED_PAIR_COUNT} recurrence component/hook manifest pairs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
