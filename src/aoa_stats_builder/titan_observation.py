from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .receipt_abi import ReceiptValidationError


TITAN_INCARNATION_SUMMARY_REF = "generated:titan-incarnation-summary:reference"


def _mapping_entries(
    payload: Mapping[str, Any], *, key: str, label: str
) -> tuple[Mapping[str, Any], ...]:
    raw_entries = payload.get(key)
    if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, (str, bytes)):
        raise ReceiptValidationError(f"{label} {key} must be an array")
    entries: list[Mapping[str, Any]] = []
    for index, raw_entry in enumerate(raw_entries):
        if not isinstance(raw_entry, Mapping):
            raise ReceiptValidationError(f"{label} {key}[{index}] must be an object")
        entries.append(raw_entry)
    if not entries:
        raise ReceiptValidationError(f"{label} {key} must not be empty")
    return tuple(entries)


def _entries_by_name(
    entries: Sequence[Mapping[str, Any]], *, name_key: str, label: str
) -> dict[str, Mapping[str, Any]]:
    by_name: dict[str, Mapping[str, Any]] = {}
    for index, entry in enumerate(entries):
        name = entry.get(name_key)
        if not isinstance(name, str) or not name.strip():
            raise ReceiptValidationError(
                f"{label}[{index}] {name_key} must be a non-empty string"
            )
        if name in by_name:
            raise ReceiptValidationError(f"{label} contains duplicate Titan {name!r}")
        by_name[name] = entry
    return by_name


def _normalized_gate(value: Any, *, label: str) -> str | None:
    if value is None or value == "none":
        return None
    if not isinstance(value, str) or not value.strip():
        raise ReceiptValidationError(f"{label} gate must be null, 'none', or non-empty")
    return value


def _state_from_operator_roster(
    payload: Mapping[str, Any],
) -> tuple[frozenset[str], frozenset[str], dict[str, str]]:
    if payload.get("version") != 1:
        raise ReceiptValidationError("aoa-agents operator roster version must be 1")
    entries = _entries_by_name(
        _mapping_entries(payload, key="titans", label="aoa-agents operator roster"),
        name_key="name",
        label="aoa-agents operator roster titans",
    )
    active: set[str] = set()
    gates: dict[str, str] = {}
    for name, entry in entries.items():
        default_active = entry.get("default_active")
        if not isinstance(default_active, bool):
            raise ReceiptValidationError(
                f"aoa-agents operator roster Titan {name!r} default_active must be boolean"
            )
        gate = _normalized_gate(
            entry.get("activation_gate"),
            label=f"aoa-agents operator roster Titan {name!r}",
        )
        if default_active:
            if gate is not None:
                raise ReceiptValidationError(
                    f"aoa-agents operator roster active Titan {name!r} cannot require a gate"
                )
            active.add(name)
        else:
            if gate is None:
                raise ReceiptValidationError(
                    f"aoa-agents operator roster inactive Titan {name!r} requires a gate"
                )
            gates[name] = gate
    return frozenset(entries), frozenset(active), gates


def _string_set(value: Any, *, label: str) -> frozenset[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ReceiptValidationError(f"{label} must be an array")
    values: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ReceiptValidationError(f"{label}[{index}] must be a non-empty string")
        values.append(item)
    if len(values) != len(set(values)):
        raise ReceiptValidationError(f"{label} must not contain duplicates")
    return frozenset(values)


def _gate_map(value: Any, *, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ReceiptValidationError(f"{label} must be an object")
    gates: dict[str, str] = {}
    for raw_name, raw_gate in value.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise ReceiptValidationError(f"{label} keys must be non-empty strings")
        gate = _normalized_gate(raw_gate, label=f"{label} Titan {raw_name!r}")
        if gate is None:
            raise ReceiptValidationError(f"{label} Titan {raw_name!r} requires a gate")
        gates[raw_name] = gate
    return gates


def _state_from_runtime_roster(
    payload: Mapping[str, Any],
) -> tuple[frozenset[str], frozenset[str], dict[str, str]]:
    if payload.get("version") != 1:
        raise ReceiptValidationError("aoa-agents runtime roster version must be 1")
    entries = _entries_by_name(
        _mapping_entries(payload, key="cohort", label="aoa-agents runtime roster"),
        name_key="name",
        label="aoa-agents runtime roster cohort",
    )
    active: set[str] = set()
    gates: dict[str, str] = {}
    for name, entry in entries.items():
        state = entry.get("default_state")
        gate = _normalized_gate(
            entry.get("gate"), label=f"aoa-agents runtime roster Titan {name!r}"
        )
        if state == "active_after_explicit_summon":
            if gate is not None:
                raise ReceiptValidationError(
                    f"aoa-agents runtime roster active Titan {name!r} cannot require a gate"
                )
            active.add(name)
        elif state == "locked":
            if gate is None:
                raise ReceiptValidationError(
                    f"aoa-agents runtime roster locked Titan {name!r} requires a gate"
                )
            gates[name] = gate
        else:
            raise ReceiptValidationError(
                f"aoa-agents runtime roster Titan {name!r} has unsupported default_state"
            )

    declared_active = _string_set(
        payload.get("default_active"), label="aoa-agents runtime roster default_active"
    )
    declared_gates = _gate_map(
        payload.get("gates"), label="aoa-agents runtime roster gates"
    )
    if declared_active != frozenset(active):
        raise ReceiptValidationError(
            "aoa-agents runtime roster default_active disagrees with cohort states"
        )
    if declared_gates != gates:
        raise ReceiptValidationError(
            "aoa-agents runtime roster gates disagree with cohort states"
        )
    if not declared_active.issubset(entries) or not set(declared_gates).issubset(entries):
        raise ReceiptValidationError(
            "aoa-agents runtime roster declarations reference unknown Titans"
        )
    return frozenset(entries), declared_active, declared_gates


def _state_from_sdk_receipt(
    payload: Mapping[str, Any],
) -> tuple[frozenset[str], frozenset[str], dict[str, str]]:
    if payload.get("schema_version") != "titan_session_receipt/v2":
        raise ReceiptValidationError(
            "aoa-sdk Titan session receipt must use titan_session_receipt/v2"
        )
    entries = _entries_by_name(
        _mapping_entries(payload, key="incarnations", label="aoa-sdk Titan session receipt"),
        name_key="titan_name",
        label="aoa-sdk Titan session receipt incarnations",
    )
    active: set[str] = set()
    gates: dict[str, str] = {}
    for name, entry in entries.items():
        state = entry.get("state")
        gate = _normalized_gate(
            entry.get("gate_required"),
            label=f"aoa-sdk Titan session receipt incarnation {name!r}",
        )
        if state == "active":
            if gate is not None:
                raise ReceiptValidationError(
                    f"aoa-sdk active Titan {name!r} cannot require a gate"
                )
            active.add(name)
        elif state == "locked":
            if gate is None:
                raise ReceiptValidationError(
                    f"aoa-sdk locked Titan {name!r} requires a gate"
                )
            gates[name] = gate
        else:
            raise ReceiptValidationError(
                f"aoa-sdk Titan {name!r} has unsupported incarnation state"
            )
    return frozenset(entries), frozenset(active), gates


def _source_refs(source_refs: Sequence[str]) -> list[str]:
    refs = list(source_refs)
    if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise ReceiptValidationError(
            "Titan Incarnation source refs must be non-empty strings"
        )
    if len(refs) != 3 or len(set(refs)) != 3:
        raise ReceiptValidationError(
            "Titan Incarnation requires three unique owner-example source refs"
        )
    return refs


def build_titan_incarnation_summary(
    operator_roster: Mapping[str, Any],
    runtime_roster: Mapping[str, Any],
    session_receipt: Mapping[str, Any],
    *,
    source_refs: Sequence[str],
) -> dict[str, Any]:
    operator_state = _state_from_operator_roster(operator_roster)
    runtime_state = _state_from_runtime_roster(runtime_roster)
    sdk_state = _state_from_sdk_receipt(session_receipt)
    if not (operator_state[0] == runtime_state[0] == sdk_state[0]):
        raise ReceiptValidationError(
            "Titan Incarnation owner examples disagree on Titan identities"
        )
    if not (operator_state[1] == runtime_state[1] == sdk_state[1]):
        raise ReceiptValidationError(
            "Titan Incarnation owner examples disagree on active Titans"
        )
    if not (operator_state[2] == runtime_state[2] == sdk_state[2]):
        raise ReceiptValidationError(
            "Titan Incarnation owner examples disagree on gate assignments"
        )

    names, active, gates = operator_state
    if len(active) + len(gates) != len(names):
        raise ReceiptValidationError(
            "Titan Incarnation active and gated partitions must conserve identities"
        )
    return {
        "schema_version": "titan_incarnation_summary/v1",
        "summary_ref": TITAN_INCARNATION_SUMMARY_REF,
        "source_receipt_refs": _source_refs(source_refs),
        "counts": {
            "seeded_titans": len(names),
            "default_active": len(active),
            "locked_by_gate": len(gates),
        },
    }
