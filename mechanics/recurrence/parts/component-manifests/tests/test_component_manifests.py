from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = PART_ROOT / "scripts" / "validate_component_manifests.py"
SPEC = importlib.util.spec_from_file_location("validate_component_manifests", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


def load(relative_path: str) -> dict:
    payload = json.loads((PART_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_live_component_manifest_contract_passes() -> None:
    assert validator.validate(REPO_ROOT, PART_ROOT) == []


def test_inventory_requires_exact_component_hook_pairing(tmp_path: Path) -> None:
    components = tmp_path / "components"
    hooks = tmp_path / "hooks"
    components.mkdir()
    hooks.mkdir()
    (components / "component.example.json").write_text("{}\n", encoding="utf-8")

    issues = validator.validate_inventory(components, hooks)

    assert any("missing_hooks=['component.example']" in issue for issue in issues)


def test_pair_rejects_mismatched_hook_identity() -> None:
    component = load("manifests/components/component.agon.wave17.aoa_stats.json")
    hook = load("manifests/hooks/component.agon.wave17.aoa_stats.hooks.json")
    broken = copy.deepcopy(hook)
    broken["component_id"] = "component.agon.wrong"

    issues = validator.validate_pair_payloads(
        component,
        broken,
        expected_identity="component.agon.wave17.aoa_stats",
        label="wave17",
    )

    assert any("hook identity mismatch" in issue for issue in issues)


def test_payload_refs_reject_stale_former_root_route() -> None:
    payload = {"surfaces": ["config/agon_kag_stats_observability.seed.json"]}

    issues = validator.validate_payload_refs(
        payload,
        label="candidate.json",
        repo_root=REPO_ROOT,
    )

    assert issues == [
        "candidate.json:surfaces.0: stale former root route: "
        "config/agon_kag_stats_observability.seed.json"
    ]
