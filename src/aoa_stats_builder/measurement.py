from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
import json
from math import comb, isclose, isfinite
from typing import Any, Iterable, Mapping, Sequence


MISSING_STATES = frozenset({"missing", "unknown", "stale"})
VALUE_FIELDS = frozenset(
    {
        "number",
        "numerator",
        "denominator",
        "distribution",
        "quantile",
        "k",
        "successes",
        "attempts",
    }
)
STATISTIC_OPERATORS = {
    "count": frozenset({"none", "sum"}),
    "gauge": frozenset({"none", "weighted_mean"}),
    "rate": frozenset({"none", "weighted_mean", "ratio_of_sums"}),
    "ratio": frozenset({"none", "ratio_of_sums"}),
    "distribution": frozenset({"none", "histogram_merge"}),
    "quantile": frozenset({"none"}),
    "pass_at_k": frozenset({"none", "pass_estimate"}),
    "pass_all_k": frozenset({"none", "pass_estimate"}),
}
PRIVACY_RANK = {"public": 0, "internal": 1, "sensitive": 2}


class MeasurementError(ValueError):
    """Raised when a measurement packet would create an invalid statistic."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _identity(prefix: str, value: Any) -> str:
    digest = sha256(_canonical_json(value).encode("utf-8")).hexdigest()
    return f"{prefix}:sha256:{digest}"


def evidence_identity(packet: Mapping[str, Any]) -> str:
    """Identify owner evidence independently of its reporting rule."""

    evidence_shape = {
        "measurement_id": packet.get("measurement_id"),
        "contract_version": packet.get("contract_version"),
        "writer_repo": packet.get("writer_repo"),
        "observation_id": packet.get("observation_id"),
        "observed_at": packet.get("observed_at"),
        "object_ref": packet.get("object_ref"),
        "population": packet.get("population"),
        "sample": packet.get("sample"),
        "cohort": packet.get("cohort"),
        "window": packet.get("window"),
        "dimensions": packet.get("dimensions"),
        "provenance": packet.get("provenance"),
        "posture": packet.get("posture"),
        "progress": packet.get("progress"),
    }
    return _identity("aoa-stats-evidence", evidence_shape)


def semantic_identity(packet: Mapping[str, Any]) -> str:
    """Identify the complete statistical meaning returned by direct or MCP reads."""

    return _identity("aoa-stats-statistic", packet)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _finite_number(value: Any) -> bool:
    return _is_number(value) and isfinite(float(value))


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _dimension_contracts(contract: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    dimensions = contract.get("dimensions")
    if not isinstance(dimensions, Mapping):
        return {}
    allowed = dimensions.get("allowed")
    if not isinstance(allowed, Sequence) or isinstance(allowed, (str, bytes)):
        return {}
    result: dict[str, Mapping[str, Any]] = {}
    for entry in allowed:
        if isinstance(entry, Mapping) and isinstance(entry.get("name"), str):
            result[entry["name"]] = entry
    return result


def validate_contract_semantics(contract: Mapping[str, Any]) -> list[str]:
    """Validate cross-field rules that JSON Schema cannot express cleanly."""

    issues: list[str] = []
    measurement_id = contract.get("measurement_id")
    owner_repo = contract.get("owner_repo")
    if isinstance(measurement_id, str) and isinstance(owner_repo, str):
        writer_prefix = measurement_id.partition("/")[0]
        if writer_prefix != owner_repo:
            issues.append("measurement_id prefix must equal owner_repo")

    missingness = contract.get("missingness")
    if isinstance(missingness, Mapping):
        states = missingness.get("states")
        if isinstance(states, list) and set(states) != MISSING_STATES:
            issues.append("missingness.states must contain missing, unknown, and stale")

    dimensions = contract.get("dimensions")
    if isinstance(dimensions, Mapping):
        allowed = _dimension_contracts(contract)
        raw_allowed = dimensions.get("allowed")
        if isinstance(raw_allowed, list) and len(allowed) != len(raw_allowed):
            issues.append("dimension names must be unique")
        prohibited = dimensions.get("prohibited")
        if isinstance(prohibited, list) and set(allowed).intersection(prohibited):
            issues.append("a dimension cannot be both allowed and prohibited")

        privacy = contract.get("privacy")
        sensitive_allowed = (
            privacy.get("sensitive_dimensions_allowed")
            if isinstance(privacy, Mapping)
            else None
        )
        if sensitive_allowed is False and any(
            entry.get("sensitivity") == "sensitive" for entry in allowed.values()
        ):
            issues.append(
                "sensitive dimensions require privacy.sensitive_dimensions_allowed"
            )

    statistic = contract.get("statistic")
    aggregation = contract.get("aggregation")
    operator = aggregation.get("operator") if isinstance(aggregation, Mapping) else None
    allowed_operators = STATISTIC_OPERATORS.get(statistic)
    if allowed_operators is not None and operator not in allowed_operators:
        issues.append(f"aggregation operator {operator!r} is invalid for {statistic!r}")

    uncertainty = contract.get("uncertainty")
    if isinstance(uncertainty, Mapping):
        methods = uncertainty.get("methods")
        if uncertainty.get("required") is True and not methods:
            issues.append("required uncertainty must name at least one method")

    privacy = contract.get("privacy")
    if isinstance(privacy, Mapping) and privacy.get("raw_content_allowed") is not False:
        issues.append("raw_content_allowed must remain false")

    return issues


def _validate_evidence_refs(packet: Mapping[str, Any], issues: list[str]) -> None:
    provenance = packet.get("provenance")
    if not isinstance(provenance, Mapping):
        return
    refs = provenance.get("evidence_refs")
    if not isinstance(refs, list):
        return
    for index, entry in enumerate(refs):
        if not isinstance(entry, Mapping):
            continue
        ref = entry.get("ref")
        if not isinstance(ref, str):
            continue
        lowered = ref.lower()
        if ref.startswith(("/", "~")):
            issues.append(f"provenance.evidence_refs[{index}] uses a host-local path")
        if ".aoa/sessions" in lowered or "transcript" in lowered:
            issues.append(
                f"provenance.evidence_refs[{index}] points to raw session material"
            )


def _validate_observed_value(
    contract: Mapping[str, Any], packet: Mapping[str, Any], issues: list[str]
) -> None:
    value = packet.get("value")
    sample = packet.get("sample")
    if not isinstance(value, Mapping) or not isinstance(sample, Mapping):
        return

    kind = value.get("kind")
    number = value.get("number")
    sample_size = sample.get("size")
    missingness = contract.get("missingness")
    zero_is_observation = (
        missingness.get("zero_is_observation")
        if isinstance(missingness, Mapping)
        else None
    )

    if kind == "count":
        if not isinstance(number, int) or isinstance(number, bool) or number < 0:
            issues.append("observed count requires a non-negative integer number")
    elif kind in {"gauge", "rate"}:
        if not _finite_number(number):
            issues.append(f"observed {kind} requires a finite number")
    elif kind == "ratio":
        numerator = value.get("numerator")
        denominator = value.get("denominator")
        if not _finite_number(numerator):
            issues.append("observed ratio requires a finite numerator")
        if not _finite_number(denominator) or float(denominator) <= 0:
            issues.append("observed ratio requires a positive denominator")
        if _finite_number(numerator) and _finite_number(denominator):
            expected = float(numerator) / float(denominator)
            if not _finite_number(number) or not isclose(
                float(number), expected, rel_tol=1e-12, abs_tol=1e-12
            ):
                issues.append("ratio number must equal numerator / denominator")
    elif kind == "distribution":
        distribution = value.get("distribution")
        if not isinstance(distribution, Mapping):
            issues.append("observed distribution requires distribution summary")
        else:
            count = distribution.get("count")
            minimum = distribution.get("minimum")
            maximum = distribution.get("maximum")
            quantiles = distribution.get("quantiles")
            if not isinstance(count, int) or isinstance(count, bool) or count < 1:
                issues.append("distribution count must be a positive integer")
            elif isinstance(sample_size, int) and count != sample_size:
                issues.append("distribution count must equal sample.size")
            if not _finite_number(minimum) or not _finite_number(maximum):
                issues.append("distribution bounds must be finite")
            elif float(minimum) > float(maximum):
                issues.append("distribution minimum must not exceed maximum")
            if isinstance(quantiles, list):
                previous_q = -1.0
                seen_q: set[float] = set()
                for entry in quantiles:
                    if not isinstance(entry, Mapping):
                        continue
                    q = entry.get("q")
                    quantile_value = entry.get("value")
                    if not _finite_number(q) or not 0 <= float(q) <= 1:
                        issues.append("distribution quantile q must be in [0, 1]")
                        continue
                    if float(q) in seen_q or float(q) < previous_q:
                        issues.append("distribution quantiles must be unique and ordered")
                    seen_q.add(float(q))
                    previous_q = float(q)
                    if not _finite_number(quantile_value):
                        issues.append("distribution quantile value must be finite")
                    elif _finite_number(minimum) and _finite_number(maximum) and not (
                        float(minimum) <= float(quantile_value) <= float(maximum)
                    ):
                        issues.append("distribution quantile lies outside its bounds")
    elif kind == "quantile":
        quantile = value.get("quantile")
        if not isinstance(quantile, Mapping):
            issues.append("observed quantile requires q and value")
        elif not (
            _finite_number(quantile.get("q"))
            and 0 <= float(quantile["q"]) <= 1
            and _finite_number(quantile.get("value"))
        ):
            issues.append("quantile requires finite value and q in [0, 1]")
        if not isinstance(sample_size, int) or sample_size < 1:
            issues.append("observed quantile requires a non-empty sample")
    elif kind in {"pass_at_k", "pass_all_k"}:
        successes = value.get("successes")
        attempts = value.get("attempts")
        k = value.get("k")
        if not all(
            isinstance(item, int) and not isinstance(item, bool)
            for item in (successes, attempts, k)
        ):
            issues.append(f"{kind} requires integer successes, attempts, and k")
        elif attempts < 1 or successes < 0 or successes > attempts or not 1 <= k <= attempts:
            issues.append(f"{kind} requires 0 <= successes <= attempts and 1 <= k <= attempts")
        else:
            if sample_size != attempts:
                issues.append(f"{kind} attempts must equal sample.size")
            expected = pass_estimate(
                successes=successes,
                attempts=attempts,
                k=k,
                statistic=kind,
            )
            if not _finite_number(number) or not isclose(
                float(number), expected, rel_tol=1e-12, abs_tol=1e-12
            ):
                issues.append(f"{kind} number does not match its exact estimate")

    if zero_is_observation is False and _finite_number(number) and float(number) == 0:
        issues.append("zero is not an admitted observation for this contract")


def validate_packet_semantics(
    contract: Mapping[str, Any], packet: Mapping[str, Any]
) -> list[str]:
    """Validate one packet against its owner contract without doing I/O."""

    issues = [f"contract: {issue}" for issue in validate_contract_semantics(contract)]

    comparisons = (
        ("measurement_id", "measurement_id"),
        ("contract_version", "contract_version"),
        ("writer_repo", "owner_repo"),
    )
    for packet_field, contract_field in comparisons:
        if packet.get(packet_field) != contract.get(contract_field):
            issues.append(f"{packet_field} does not match contract {contract_field}")

    object_ref = packet.get("object_ref")
    if isinstance(object_ref, Mapping) and object_ref.get("kind") != contract.get(
        "object_kind"
    ):
        issues.append("object_ref.kind does not match contract object_kind")

    window = packet.get("window")
    contract_window = contract.get("window")
    if isinstance(window, Mapping) and isinstance(contract_window, Mapping):
        if window.get("temporality") != contract_window.get("temporality"):
            issues.append("window temporality does not match contract")
        start = _parse_datetime(window.get("start"))
        end = _parse_datetime(window.get("end"))
        if (window.get("start") is None) != (window.get("end") is None):
            issues.append("window start and end must both be known or both be null")
        if start is not None and end is not None and end < start:
            issues.append("window end precedes start")

    population = packet.get("population")
    sample = packet.get("sample")
    if isinstance(population, Mapping) and isinstance(sample, Mapping):
        population_size = population.get("size")
        sample_size = sample.get("size")
        if (
            isinstance(population_size, int)
            and isinstance(sample_size, int)
            and sample_size > population_size
        ):
            issues.append("sample.size exceeds known population.size")

    dimensions = packet.get("dimensions")
    allowed = _dimension_contracts(contract)
    if isinstance(dimensions, Mapping):
        unknown_dimensions = set(dimensions) - set(allowed)
        if unknown_dimensions:
            issues.append(f"dimensions are not allowed: {sorted(unknown_dimensions)!r}")
        privacy = contract.get("privacy")
        sensitive_allowed = (
            privacy.get("sensitive_dimensions_allowed")
            if isinstance(privacy, Mapping)
            else False
        )
        if not sensitive_allowed and any(
            allowed.get(name, {}).get("sensitivity") == "sensitive"
            for name in dimensions
        ):
            issues.append("packet uses a sensitive dimension forbidden by the contract")

    value = packet.get("value")
    if isinstance(value, Mapping):
        if value.get("kind") != contract.get("statistic"):
            issues.append("value.kind does not match contract statistic")
        unit = contract.get("unit")
        expected_unit = unit.get("symbol") if isinstance(unit, Mapping) else None
        if value.get("unit") != expected_unit:
            issues.append("value.unit does not match contract unit")
        status = value.get("status")
        if status in MISSING_STATES:
            present_value_fields = sorted(VALUE_FIELDS.intersection(value))
            if present_value_fields:
                issues.append(
                    f"{status} packet must not carry numeric value fields: {present_value_fields!r}"
                )
            if not value.get("reason"):
                issues.append(f"{status} packet requires a reason")
        elif status == "observed":
            _validate_observed_value(contract, packet, issues)

    uncertainty = packet.get("uncertainty")
    if isinstance(uncertainty, Mapping) and isinstance(sample, Mapping):
        if uncertainty.get("sample_size") != sample.get("size"):
            issues.append("uncertainty.sample_size must equal sample.size")
        lower = uncertainty.get("lower")
        upper = uncertainty.get("upper")
        if (lower is None) != (upper is None):
            issues.append("uncertainty bounds must be supplied together")
        elif _finite_number(lower) and _finite_number(upper) and float(lower) > float(upper):
            issues.append("uncertainty lower exceeds upper")
        contract_uncertainty = contract.get("uncertainty")
        if isinstance(contract_uncertainty, Mapping):
            methods = contract_uncertainty.get("methods")
            if isinstance(methods, list) and uncertainty.get("method") not in methods:
                issues.append("uncertainty method is not admitted by the contract")
            if (
                contract_uncertainty.get("required") is True
                and isinstance(value, Mapping)
                and value.get("status") == "observed"
                and uncertainty.get("status") != "estimated"
            ):
                issues.append("observed packet requires estimated uncertainty")

    provenance = packet.get("provenance")
    contract_provenance = contract.get("provenance")
    if isinstance(provenance, Mapping) and isinstance(contract_provenance, Mapping):
        if (
            contract_provenance.get("source_revision_required") is True
            and provenance.get("source_revision") is None
        ):
            issues.append("source_revision is required by the contract")
    _validate_evidence_refs(packet, issues)

    posture = packet.get("posture")
    live_state = contract.get("live_state")
    privacy = contract.get("privacy")
    if isinstance(posture, Mapping):
        if (
            isinstance(live_state, Mapping)
            and live_state.get("capability") == "reference_only"
            and posture.get("live_state") == "live"
        ):
            issues.append("reference-only contract cannot produce a live packet")
        if posture.get("raw_content_included") is not False:
            issues.append("packet must not include raw content")
        contract_privacy = (
            privacy.get("classification") if isinstance(privacy, Mapping) else None
        )
        packet_privacy = posture.get("privacy")
        if (
            contract_privacy in PRIVACY_RANK
            and packet_privacy in PRIVACY_RANK
            and PRIVACY_RANK[packet_privacy] < PRIVACY_RANK[contract_privacy]
        ):
            issues.append("packet privacy is weaker than the contract")
        if isinstance(value, Mapping):
            expected_freshness = {
                "stale": "stale",
                "unknown": "unknown",
            }.get(value.get("status"))
            if expected_freshness and posture.get("freshness") != expected_freshness:
                issues.append(
                    f"{value.get('status')} value requires {expected_freshness} freshness"
                )

    progress = packet.get("progress")
    if isinstance(progress, Mapping):
        completed = progress.get("completed")
        total = progress.get("total")
        if isinstance(completed, int) and isinstance(total, int) and completed > total:
            issues.append("progress.completed exceeds progress.total")
        if (
            progress.get("state") == "partial"
            and isinstance(completed, int)
            and isinstance(total, int)
            and completed >= total
        ):
            issues.append("partial progress must remain below a known total")

    return issues


def validate_packet_set(
    contract: Mapping[str, Any], packets: Sequence[Mapping[str, Any]]
) -> list[str]:
    """Validate packet semantics, duplicate writers, and dimension cardinality."""

    issues: list[str] = []
    observation_ids: set[str] = set()
    writers: set[str] = set()
    for index, packet in enumerate(packets):
        issues.extend(
            f"packet[{index}]: {issue}"
            for issue in validate_packet_semantics(contract, packet)
        )
        observation_id = packet.get("observation_id")
        if isinstance(observation_id, str):
            if observation_id in observation_ids:
                issues.append(f"packet[{index}]: duplicate observation_id {observation_id!r}")
            observation_ids.add(observation_id)
        writer = packet.get("writer_repo")
        if isinstance(writer, str):
            writers.add(writer)
    if len(writers) > 1:
        issues.append(f"measurement has duplicate writers: {sorted(writers)!r}")

    dimensions = _dimension_contracts(contract)
    for name, dimension_contract in dimensions.items():
        values = {
            packet_dimensions[name]
            for packet in packets
            if isinstance((packet_dimensions := packet.get("dimensions")), Mapping)
            and name in packet_dimensions
        }
        maximum = dimension_contract.get("max_cardinality")
        if isinstance(maximum, int) and len(values) > maximum:
            issues.append(
                f"dimension {name!r} cardinality {len(values)} exceeds {maximum}"
            )
    return issues


def pass_estimate(
    *, successes: int, attempts: int, k: int, statistic: str
) -> float:
    """Return exact finite-sample pass@k or pass^k from exchangeable attempts."""

    if attempts < 1 or successes < 0 or successes > attempts or not 1 <= k <= attempts:
        raise MeasurementError(
            "pass estimate requires 0 <= successes <= attempts and 1 <= k <= attempts"
        )
    denominator = comb(attempts, k)
    if statistic == "pass_at_k":
        failures = attempts - successes
        return 1.0 - (comb(failures, k) / denominator if failures >= k else 0.0)
    if statistic == "pass_all_k":
        return comb(successes, k) / denominator if successes >= k else 0.0
    raise MeasurementError("statistic must be pass_at_k or pass_all_k")


def summarize_distribution(
    values: Iterable[int | float], *, quantiles: Sequence[float]
) -> dict[str, Any]:
    """Create a privacy-bounded distribution summary without retaining raw values."""

    ordered = sorted(float(value) for value in values)
    if not ordered or any(not isfinite(value) for value in ordered):
        raise MeasurementError("distribution input must contain finite values")
    normalized_q = [float(q) for q in quantiles]
    if any(not isfinite(q) or not 0 <= q <= 1 for q in normalized_q):
        raise MeasurementError("quantiles must be finite and in [0, 1]")
    if normalized_q != sorted(set(normalized_q)):
        raise MeasurementError("quantiles must be unique and ordered")

    def interpolate(q: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        position = q * (len(ordered) - 1)
        lower_index = int(position)
        upper_index = min(lower_index + 1, len(ordered) - 1)
        fraction = position - lower_index
        return ordered[lower_index] + (
            ordered[upper_index] - ordered[lower_index]
        ) * fraction

    return {
        "count": len(ordered),
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "quantiles": [
            {"q": q, "value": interpolate(q)} for q in normalized_q
        ],
    }


def _all_equal(values: Sequence[Any]) -> bool:
    return all(value == values[0] for value in values[1:]) if values else True


def _aggregate_value(
    operator: str, statistic: str, packets: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    values = [packet["value"] for packet in packets]
    unit = values[0]["unit"]
    if operator == "sum" and statistic == "count":
        return {
            "status": "observed",
            "kind": statistic,
            "unit": unit,
            "number": sum(value["number"] for value in values),
        }
    if operator == "weighted_mean" and statistic in {"gauge", "rate"}:
        weights = [packet["sample"]["size"] for packet in packets]
        if sum(weights) <= 0:
            raise MeasurementError("weighted mean requires a non-empty sample")
        return {
            "status": "observed",
            "kind": statistic,
            "unit": unit,
            "number": sum(
                value["number"] * weight for value, weight in zip(values, weights)
            )
            / sum(weights),
        }
    if operator == "ratio_of_sums" and statistic in {"ratio", "rate"}:
        if any(
            not _finite_number(value.get("numerator"))
            or not _finite_number(value.get("denominator"))
            for value in values
        ):
            raise MeasurementError("ratio_of_sums requires numerator and denominator")
        numerator = sum(value["numerator"] for value in values)
        denominator = sum(value["denominator"] for value in values)
        if denominator <= 0:
            raise MeasurementError("ratio_of_sums requires a positive denominator")
        return {
            "status": "observed",
            "kind": statistic,
            "unit": unit,
            "number": numerator / denominator,
            "numerator": numerator,
            "denominator": denominator,
        }
    if operator == "pass_estimate" and statistic in {"pass_at_k", "pass_all_k"}:
        ks = [value.get("k") for value in values]
        if not _all_equal(ks):
            raise MeasurementError("pass estimates require one shared k")
        successes = sum(value["successes"] for value in values)
        attempts = sum(value["attempts"] for value in values)
        k = ks[0]
        return {
            "status": "observed",
            "kind": statistic,
            "unit": unit,
            "number": pass_estimate(
                successes=successes,
                attempts=attempts,
                k=k,
                statistic=statistic,
            ),
            "successes": successes,
            "attempts": attempts,
            "k": k,
        }
    if operator == "histogram_merge":
        raise MeasurementError(
            "v1 distribution summaries do not contain a mergeable histogram"
        )
    raise MeasurementError(
        f"aggregation operator {operator!r} is not implemented for {statistic!r}"
    )


def aggregate_packets(
    contract: Mapping[str, Any], packets: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Aggregate compatible observed packets without strengthening their authority."""

    if not packets:
        raise MeasurementError("at least one packet is required")
    issues = validate_packet_set(contract, packets)
    if issues:
        raise MeasurementError("; ".join(issues))
    if any(packet["value"]["status"] != "observed" for packet in packets):
        raise MeasurementError(
            "missing, unknown, or stale packets cannot be coerced into aggregation"
        )

    aggregation = contract["aggregation"]
    operator = aggregation["operator"]
    if operator == "none":
        raise MeasurementError("contract does not admit aggregation")
    if contract["uncertainty"]["required"] is True:
        raise MeasurementError(
            "aggregation cannot discard a required uncertainty estimate"
        )
    across = set(aggregation["across"])

    compatibility_fields = {
        "population": [packet["population"]["id"] for packet in packets],
        "cohort": [packet["cohort"] for packet in packets],
        "window": [packet["window"]["id"] for packet in packets],
        "dimension": [packet["dimensions"] for packet in packets],
    }
    for field, values in compatibility_fields.items():
        if not _all_equal(values) and field not in across:
            raise MeasurementError(
                f"contract does not admit aggregation across {field}"
            )
    definition_refs = [packet["population"]["definition_ref"] for packet in packets]
    if not _all_equal(definition_refs):
        raise MeasurementError("population definitions are not comparable")
    reporting_rules = [packet["reporting_rule"] for packet in packets]
    if not _all_equal(reporting_rules):
        raise MeasurementError("reporting-rule versions are not compatible")

    value = _aggregate_value(operator, contract["statistic"], packets)
    seed = {
        "measurement_id": contract["measurement_id"],
        "contract_version": contract["contract_version"],
        "operator": operator,
        "observation_ids": sorted(packet["observation_id"] for packet in packets),
    }
    aggregate_ref = _identity("derived", seed)
    result = deepcopy(dict(packets[0]))
    result["observation_id"] = aggregate_ref
    result["observed_at"] = max(packet["observed_at"] for packet in packets)
    result["object_ref"] = {
        "kind": contract["object_kind"],
        "id": aggregate_ref,
        "version": contract["contract_version"],
    }
    population_sizes = [packet["population"]["size"] for packet in packets]
    result["population"] = {
        "id": _identity("population", sorted(compatibility_fields["population"])),
        "definition_ref": definition_refs[0],
        "size": (
            sum(population_sizes)
            if all(isinstance(size, int) for size in population_sizes)
            else None
        ),
    }
    result["sample"] = {
        "size": sum(packet["sample"]["size"] for packet in packets),
        "selection": "derived union of compatible owner samples",
    }
    result["cohort"] = packets[0]["cohort"] if _all_equal(compatibility_fields["cohort"]) else None

    starts = [_parse_datetime(packet["window"]["start"]) for packet in packets]
    ends = [_parse_datetime(packet["window"]["end"]) for packet in packets]
    result["window"] = {
        "id": _identity("window", sorted(compatibility_fields["window"])),
        "start": min(start for start in starts if start is not None).isoformat().replace(
            "+00:00", "Z"
        )
        if all(start is not None for start in starts)
        else None,
        "end": max(end for end in ends if end is not None).isoformat().replace(
            "+00:00", "Z"
        )
        if all(end is not None for end in ends)
        else None,
        "temporality": contract["window"]["temporality"],
    }
    result["dimensions"] = (
        dict(packets[0]["dimensions"])
        if _all_equal(compatibility_fields["dimension"])
        else {}
    )
    result["value"] = value
    result["uncertainty"] = {
        "status": "not_estimated",
        "sample_size": result["sample"]["size"],
        "method": "not_estimated",
        "reason": "aggregation does not invent an uncertainty estimate",
    }
    evidence_refs: list[dict[str, Any]] = []
    for packet in packets:
        for evidence_ref in packet["provenance"]["evidence_refs"]:
            if evidence_ref not in evidence_refs:
                evidence_refs.append(deepcopy(evidence_ref))
    source_revisions = [packet["provenance"]["source_revision"] for packet in packets]
    result["provenance"] = {
        "evidence_refs": evidence_refs,
        "derivation_ref": "aoa-stats:src/aoa_stats_builder/measurement.py#aggregate_packets",
        "source_revision": (
            _identity("source-set", source_revisions)
            if all(isinstance(revision, str) for revision in source_revisions)
            else None
        ),
    }
    result["posture"] = {
        "freshness": "current",
        "live_state": "live"
        if all(packet["posture"]["live_state"] == "live" for packet in packets)
        else "reference",
        "privacy": max(
            (packet["posture"]["privacy"] for packet in packets),
            key=PRIVACY_RANK.__getitem__,
        ),
        "raw_content_included": False,
    }
    totals = [packet["progress"]["total"] for packet in packets]
    result["progress"] = {
        "state": "terminal"
        if all(packet["progress"]["state"] == "terminal" for packet in packets)
        else "partial",
        "completed": sum(packet["progress"]["completed"] for packet in packets),
        "total": sum(totals) if all(isinstance(total, int) for total in totals) else None,
    }
    return result
