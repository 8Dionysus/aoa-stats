from __future__ import annotations

from copy import deepcopy
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import sys
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker
import pytest


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.receipt_abi import ReceiptValidationError  # noqa: E402
from aoa_stats_builder import titan_observation  # noqa: E402
from aoa_stats_builder.titan_observation_sources import (  # noqa: E402
    AGENTS_OPERATOR_ROSTER,
    AGENTS_RUNTIME_ROSTER,
    SDK_SESSION_RECEIPT,
    TitanIncarnationInputBundle,
    load_titan_incarnation_reference_bundle,
)


SOURCE_REFS = (
    f"aoa-agents/{AGENTS_OPERATOR_ROSTER.as_posix()}",
    f"aoa-agents/{AGENTS_RUNTIME_ROSTER.as_posix()}",
    f"aoa-sdk/{SDK_SESSION_RECEIPT.as_posix()}",
)


def load_build_views_module():
    script_path = REPO_ROOT / "scripts" / "build_views.py"
    spec = importlib.util.spec_from_file_location("build_views_titan", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def owner_examples() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    operator = {
        "version": 1,
        "titans": [
            {"name": "Atlas", "default_active": True, "activation_gate": None},
            {"name": "Sentinel", "default_active": True, "activation_gate": None},
            {"name": "Mneme", "default_active": True, "activation_gate": None},
            {"name": "Forge", "default_active": False, "activation_gate": "mutation"},
            {"name": "Delta", "default_active": False, "activation_gate": "judgment"},
        ],
    }
    runtime = {
        "version": 1,
        "cohort": [
            {"name": "Atlas", "default_state": "active_after_explicit_summon", "gate": "none"},
            {"name": "Sentinel", "default_state": "active_after_explicit_summon", "gate": "none"},
            {"name": "Mneme", "default_state": "active_after_explicit_summon", "gate": "none"},
            {"name": "Forge", "default_state": "locked", "gate": "mutation"},
            {"name": "Delta", "default_state": "locked", "gate": "judgment"},
        ],
        "default_active": ["Atlas", "Sentinel", "Mneme"],
        "gates": {"Forge": "mutation", "Delta": "judgment"},
    }
    session = {
        "schema_version": "titan_session_receipt/v2",
        "incarnations": [
            {"titan_name": "Atlas", "state": "active", "gate_required": None},
            {"titan_name": "Sentinel", "state": "active", "gate_required": None},
            {"titan_name": "Mneme", "state": "active", "gate_required": None},
            {"titan_name": "Forge", "state": "locked", "gate_required": "mutation"},
            {"titan_name": "Delta", "state": "locked", "gate_required": "judgment"},
        ],
    }
    return operator, runtime, session


def build_incarnation(
    examples: tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    operator, runtime, session = examples or owner_examples()
    return titan_observation.build_titan_incarnation_summary(
        operator, runtime, session, source_refs=SOURCE_REFS
    )


def assert_schema_valid(name: str, summary: dict[str, Any]) -> None:
    schema = json.loads((REPO_ROOT / "schemas" / name).read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(summary)


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def test_root_incarnation_facade_delegates_to_core() -> None:
    facade = load_build_views_module()
    operator, runtime, session = owner_examples()
    bundle = TitanIncarnationInputBundle(
        operator_roster=operator,
        runtime_roster=runtime,
        session_receipt=session,
        source_refs=SOURCE_REFS,
    )
    incarnation_calls: list[tuple[Any, Any, Any, tuple[str, ...]]] = []
    def tracked_incarnation(
        operator_roster: Any,
        runtime_roster: Any,
        session_receipt: Any,
        *,
        source_refs: tuple[str, ...],
    ) -> dict[str, Any]:
        incarnation_calls.append(
            (operator_roster, runtime_roster, session_receipt, source_refs)
        )
        return titan_observation.build_titan_incarnation_summary(
            operator_roster,
            runtime_roster,
            session_receipt,
            source_refs=source_refs,
        )

    facade.titan_incarnation_input_bundle = lambda: bundle
    facade.build_titan_incarnation_summary_from_inputs = tracked_incarnation

    assert facade.build_titan_incarnation_summary() == build_incarnation()
    assert incarnation_calls == [
        (bundle.operator_roster, bundle.runtime_roster, bundle.session_receipt, SOURCE_REFS)
    ]


def test_incarnation_derives_exact_coherent_reference_counts() -> None:
    summary = build_incarnation()

    assert summary == {
        "schema_version": "titan_incarnation_summary/v1",
        "summary_ref": "generated:titan-incarnation-summary:reference",
        "source_receipt_refs": list(SOURCE_REFS),
        "counts": {
            "seeded_titans": 5,
            "default_active": 3,
            "locked_by_gate": 2,
        },
    }
    assert summary["counts"]["default_active"] + summary["counts"]["locked_by_gate"] == summary["counts"]["seeded_titans"]
    assert_schema_valid("titan_incarnation_summary.schema.json", summary)


def test_incarnation_is_invariant_to_each_owner_roster_order() -> None:
    original = owner_examples()
    expected = build_incarnation(original)
    for payload_index, entry_key in ((0, "titans"), (1, "cohort"), (2, "incarnations")):
        for ordered_entries in permutations(original[payload_index][entry_key]):
            varied = deepcopy(original)
            varied[payload_index][entry_key] = list(ordered_entries)
            assert build_incarnation(varied) == expected


Mutation = Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], None]


def duplicate_operator(
    operator: dict[str, Any], runtime: dict[str, Any], session: dict[str, Any]
) -> None:
    operator["titans"].append(deepcopy(operator["titans"][0]))


def omit_runtime_titan(
    operator: dict[str, Any], runtime: dict[str, Any], session: dict[str, Any]
) -> None:
    runtime["cohort"] = runtime["cohort"][:-1]
    runtime["gates"].pop("Delta")


def drift_sdk_active_state(
    operator: dict[str, Any], runtime: dict[str, Any], session: dict[str, Any]
) -> None:
    session["incarnations"][-1]["state"] = "active"
    session["incarnations"][-1]["gate_required"] = None


def drift_operator_gate(
    operator: dict[str, Any], runtime: dict[str, Any], session: dict[str, Any]
) -> None:
    operator["titans"][-1]["activation_gate"] = "mutation"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (duplicate_operator, "duplicate Titan"),
        (omit_runtime_titan, "disagree on Titan identities"),
        (drift_sdk_active_state, "disagree on active Titans"),
        (drift_operator_gate, "disagree on gate assignments"),
    ],
)
def test_incarnation_rejects_cross_owner_drift(
    mutation: Mutation, message: str
) -> None:
    operator, runtime, session = owner_examples()
    mutation(operator, runtime, session)

    with pytest.raises(ReceiptValidationError, match=message):
        build_incarnation((operator, runtime, session))


def test_incarnation_does_not_mutate_owner_examples_or_refs() -> None:
    examples = owner_examples()
    original_examples = deepcopy(examples)
    refs = list(SOURCE_REFS)
    original_refs = list(refs)

    titan_observation.build_titan_incarnation_summary(
        *examples, source_refs=refs
    )

    assert examples == original_examples
    assert refs == original_refs


def test_source_adapter_uses_exact_owner_paths_and_frozen_bundle(tmp_path: Path) -> None:
    agents_root = tmp_path / "aoa-agents"
    sdk_root = tmp_path / "aoa-sdk"
    operator, runtime, session = owner_examples()
    for root, relative_path, payload in (
        (agents_root, AGENTS_OPERATOR_ROSTER, operator),
        (agents_root, AGENTS_RUNTIME_ROSTER, runtime),
        (sdk_root, SDK_SESSION_RECEIPT, session),
    ):
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    bundle = load_titan_incarnation_reference_bundle(
        agents_root=agents_root, sdk_root=sdk_root
    )

    assert bundle.source_refs == SOURCE_REFS
    assert build_incarnation(bundle.mutable_parts()[:3]) == build_incarnation()
    with pytest.raises(TypeError):
        bundle.operator_roster["version"] = 2


def test_summon_retirement_has_no_active_builder_output_or_catalog_entry() -> None:
    facade = load_build_views_module()
    retired = json.loads(
        (
            REPO_ROOT
            / "stats/read-models/retired/titan_summon_summary.profile.json"
        ).read_text(encoding="utf-8")
    )
    catalog = json.loads(
        (REPO_ROOT / "generated/summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )

    assert not hasattr(facade, "build_titan_summon_summary")
    assert not hasattr(
        titan_observation,
        "build_titan_summon_no_observed_ledger_baseline",
    )
    assert not (REPO_ROOT / retired["retired_surface_ref"]).exists()
    assert not (
        REPO_ROOT / "stats/read-models/active/titan_summon_summary.profile.json"
    ).exists()
    assert (REPO_ROOT / retired["schema_ref"]).is_file()
    assert retired["replacement_ref"] is None
    assert retired["former_mechanic_routes"] == [
        "mechanics/titan/parts/incarnation-summon"
    ]
    assert "titan_summon_summary" not in {
        entry["name"] for entry in catalog["surfaces"]
    }


def test_committed_titan_incarnation_output_matches_exact_core_bytes() -> None:
    assert stable_json(build_incarnation()) == (
        REPO_ROOT / "generated" / "titan_incarnation_summary.min.json"
    ).read_text(encoding="utf-8")
