from __future__ import annotations

import importlib.util
from pathlib import Path


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
PUBLIC_ENTRYPOINT = REPO_ROOT / "scripts" / "validate_abyss_machine_summary_catalog_bundle.py"


def load_public_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_abyss_machine_summary_catalog_bundle",
        PUBLIC_ENTRYPOINT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeArtifactBundles:
    def __init__(self, response: dict) -> None:
        self.response = response

    def trust_gate(self, *_args, **_kwargs) -> dict:
        return self.response


def test_public_entrypoint_delegates_to_part_local_validator() -> None:
    validator = load_public_validator()

    assert validator.CANONICAL_IMPLEMENTATION == (
        PART_ROOT / "scripts" / "validate_abyss_machine_summary_catalog_bundle.py"
    )


def test_pre_materialization_gate_denies_only_missing_subject_store() -> None:
    validator = load_public_validator()
    response = {
        "ok": False,
        "verdict": "deny",
        "blockers": [validator.REQUIRED_SUBJECT_STORE_BLOCKER],
        "decision": {
            "model": "fail_closed_consumer_admission",
            "allow": False,
            "blockers": [validator.REQUIRED_SUBJECT_STORE_BLOCKER],
        },
        "inspected_claims": {
            "registry_latest": {"selected_record_is_latest": True},
            "controls": {"required_controls_missing": []},
            "source": {"source_repo_matched": True},
            "trust_root": {"trust_root_mode_matched": True},
            "verification": {"ok": True},
            "artifact_subject_store": {"required": True, "ok": False},
        },
    }
    registry = {"promoted": {"record": {"subject_digest": "sha256:subject"}}}

    accepted = validator._trust_gate_pre_materialization_state(
        FakeArtifactBundles(response),
        Path("registry"),
        registry,
    )
    assert accepted["ok"] is True
    assert accepted["mode"] == "deny_until_subject_store_materialized"

    response["decision"]["blockers"].append("unexpected_trust_regression")
    rejected = validator._trust_gate_pre_materialization_state(
        FakeArtifactBundles(response),
        Path("registry"),
        registry,
    )
    assert rejected["ok"] is False
    assert rejected["unexpected_pre_materialization_blockers"] == [
        "unexpected_trust_regression"
    ]
