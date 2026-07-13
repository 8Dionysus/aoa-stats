from __future__ import annotations

import importlib.util
import json
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


def test_manifest_requires_registry_lifecycle_and_sbom_lite() -> None:
    manifest = json.loads(
        (
            REPO_ROOT
            / "manifests/artifact_bundles/summary_surface_catalog.bundle.json"
        ).read_text(encoding="utf-8")
    )

    assert manifest["artifact_class"] == "derived_observability_readmodel_catalog"
    assert manifest["public_safe"] is True
    assert (
        manifest["artifact_source"]["kind"]
        == "generated_observability_readmodel_catalog"
    )
    assert manifest["lifecycle"]["initial_state"] == "candidate"
    assert "release-ready" in manifest["lifecycle"]["promotion_path"]
    assert manifest["consumer_contract"]["registry_required"] is True
    command_text = "\n".join(manifest["consumer_command"])
    assert "evidence-promote" in command_text
    assert "materialize-subjects" in command_text
    assert "trust-gate" in command_text
    assert "registry-latest" in command_text
    assert "--consumer-ref aoa-stats:summary-surface-catalog" in command_text
    assert {item["role"] for item in manifest["artifact_subjects"]} == {
        "authority_doc",
        "schema",
        "summary_surface_catalog",
    }
    assert "--source-repo aoa-stats" in command_text
    assert "--trust-root-mode host_managed" in command_text
    assert manifest["consumer_contract"]["subject_store_required"] is True
    assert (
        manifest["consumer_contract"]["admission_gate"]
        == "fail_closed_consumer_admission"
    )
