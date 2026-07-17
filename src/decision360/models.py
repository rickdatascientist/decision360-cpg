"""Domain contracts for the deterministic Decision360 reference slice."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def to_primitive(value: Any) -> Any:
    """Convert domain objects to JSON-safe primitives without losing decimal text."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return to_primitive(asdict(value))
    if isinstance(value, dict):
        return {key: to_primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_primitive(item) for item in value]
    return value


class Action(str, Enum):
    EXPEDITE = "expedite"
    MONITOR = "monitor"


@dataclass(frozen=True)
class EvidenceRef:
    field: str
    source: str
    observed_at: str
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceRef":
        return cls(
            field=str(data["field"]),
            source=str(data["source"]),
            observed_at=str(data["observed_at"]),
            note=str(data.get("note", "")),
        )


@dataclass(frozen=True)
class DecisionCase:
    case_id: str
    sku: str
    period: str
    forecast_units: Decimal
    available_inventory_units: Decimal
    confirmed_inbound_units: Decimal
    unit_margin: Decimal
    expedite_unit_cost: Decimal
    max_expedite_units: Decimal
    evidence: tuple[EvidenceRef, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DecisionCase":
        return cls(
            case_id=str(data["case_id"]),
            sku=str(data["sku"]),
            period=str(data["period"]),
            forecast_units=decimal(data["forecast_units"]),
            available_inventory_units=decimal(data["available_inventory_units"]),
            confirmed_inbound_units=decimal(data["confirmed_inbound_units"]),
            unit_margin=decimal(data["unit_margin"]),
            expedite_unit_cost=decimal(data["expedite_unit_cost"]),
            max_expedite_units=decimal(data["max_expedite_units"]),
            evidence=tuple(EvidenceRef.from_dict(item) for item in data.get("evidence", [])),
        )


@dataclass(frozen=True)
class Policy:
    min_shortfall_ratio: Decimal = Decimal("0.05")
    min_net_benefit: Decimal = Decimal("0")
    allow_expedite: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Policy":
        data = data or {}
        return cls(
            min_shortfall_ratio=decimal(data.get("min_shortfall_ratio", "0.05")),
            min_net_benefit=decimal(data.get("min_net_benefit", "0")),
            allow_expedite=bool(data.get("allow_expedite", True)),
        )


@dataclass(frozen=True)
class Scenario:
    name: str
    action_units: Decimal
    residual_shortfall_units: Decimal
    estimated_lost_margin: Decimal
    incremental_cost: Decimal
    estimated_net_benefit: Decimal


@dataclass(frozen=True)
class Recommendation:
    recommendation_id: str
    action: Action
    action_units: Decimal
    reason_codes: tuple[str, ...]
    human_approval_required: bool = True


@dataclass(frozen=True)
class Evaluation:
    evaluation_id: str
    generated_at: str
    case: DecisionCase
    policy: Policy
    projected_supply_units: Decimal
    coverage_ratio: Decimal
    shortfall_units: Decimal
    shortfall_ratio: Decimal
    scenarios: tuple[Scenario, ...]
    recommendation: Recommendation
    assumptions: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def new(
        cls,
        *,
        case: DecisionCase,
        policy: Policy,
        projected_supply_units: Decimal,
        coverage_ratio: Decimal,
        shortfall_units: Decimal,
        shortfall_ratio: Decimal,
        scenarios: tuple[Scenario, ...],
        recommendation: Recommendation,
        assumptions: tuple[str, ...],
    ) -> "Evaluation":
        return cls(
            evaluation_id=str(uuid4()),
            generated_at=utc_now(),
            case=case,
            policy=policy,
            projected_supply_units=projected_supply_units,
            coverage_ratio=coverage_ratio,
            shortfall_units=shortfall_units,
            shortfall_ratio=shortfall_ratio,
            scenarios=scenarios,
            recommendation=recommendation,
            assumptions=assumptions,
        )


def new_recommendation(action: Action, units: Decimal, reasons: tuple[str, ...]) -> Recommendation:
    return Recommendation(str(uuid4()), action, units, reasons)
