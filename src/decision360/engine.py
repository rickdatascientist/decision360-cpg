"""Transparent reference calculations for one synthetic SKU shortfall decision."""

from __future__ import annotations

from decimal import Decimal

from .models import Action, DecisionCase, Evaluation, Policy, Scenario, new_recommendation


REQUIRED_EVIDENCE_FIELDS = {
    "forecast_units",
    "available_inventory_units",
    "confirmed_inbound_units",
    "unit_margin",
    "expedite_unit_cost",
    "max_expedite_units",
}


class DecisionInputError(ValueError):
    """The reference case is incomplete or internally invalid."""


def _validate(case: DecisionCase, policy: Policy) -> None:
    numeric_fields = {
        "forecast_units": case.forecast_units,
        "available_inventory_units": case.available_inventory_units,
        "confirmed_inbound_units": case.confirmed_inbound_units,
        "unit_margin": case.unit_margin,
        "expedite_unit_cost": case.expedite_unit_cost,
        "max_expedite_units": case.max_expedite_units,
        "min_shortfall_ratio": policy.min_shortfall_ratio,
        "min_net_benefit": policy.min_net_benefit,
    }
    non_finite = [name for name, value in numeric_fields.items() if not value.is_finite()]
    if non_finite:
        raise DecisionInputError(f"Non-finite values are not allowed: {', '.join(sorted(non_finite))}")
    negative = [name for name, value in numeric_fields.items() if value < 0]
    if negative:
        raise DecisionInputError(f"Negative values are not allowed: {', '.join(sorted(negative))}")

    provided = {item.field for item in case.evidence if item.source and item.observed_at}
    missing = sorted(REQUIRED_EVIDENCE_FIELDS - provided)
    if missing:
        raise DecisionInputError(f"Missing evidence provenance for: {', '.join(missing)}")


def evaluate_case(case: DecisionCase, policy: Policy | None = None) -> Evaluation:
    """Evaluate no-action and expedite scenarios without a model dependency."""
    policy = policy or Policy()
    _validate(case, policy)

    projected_supply = case.available_inventory_units + case.confirmed_inbound_units
    shortfall = max(case.forecast_units - projected_supply, Decimal("0"))
    if case.forecast_units == 0:
        coverage_ratio = Decimal("1")
        shortfall_ratio = Decimal("0")
    else:
        coverage_ratio = projected_supply / case.forecast_units
        shortfall_ratio = shortfall / case.forecast_units

    no_action_lost_margin = shortfall * case.unit_margin
    no_action = Scenario(
        name="no_action",
        action_units=Decimal("0"),
        residual_shortfall_units=shortfall,
        estimated_lost_margin=no_action_lost_margin,
        incremental_cost=Decimal("0"),
        estimated_net_benefit=Decimal("0"),
    )

    expedite_units = min(shortfall, case.max_expedite_units)
    residual_shortfall = shortfall - expedite_units
    protected_margin = expedite_units * case.unit_margin
    expedite_cost = expedite_units * case.expedite_unit_cost
    net_benefit = protected_margin - expedite_cost
    expedite = Scenario(
        name="expedite",
        action_units=expedite_units,
        residual_shortfall_units=residual_shortfall,
        estimated_lost_margin=residual_shortfall * case.unit_margin,
        incremental_cost=expedite_cost,
        estimated_net_benefit=net_benefit,
    )

    reasons: list[str] = []
    if shortfall == 0:
        reasons.append("NO_PROJECTED_SHORTFALL")
    elif shortfall_ratio < policy.min_shortfall_ratio:
        reasons.append("SHORTFALL_BELOW_POLICY_THRESHOLD")
    elif not policy.allow_expedite:
        reasons.append("EXPEDITE_DISABLED_BY_POLICY")
    elif expedite_units == 0:
        reasons.append("NO_EXPEDITE_CAPACITY")
    elif net_benefit <= policy.min_net_benefit:
        reasons.append("EXPEDITE_NOT_ECONOMIC_UNDER_REFERENCE_ASSUMPTIONS")
    else:
        reasons.extend(("MATERIAL_PROJECTED_SHORTFALL", "POSITIVE_REFERENCE_NET_BENEFIT"))

    should_expedite = reasons == ["MATERIAL_PROJECTED_SHORTFALL", "POSITIVE_REFERENCE_NET_BENEFIT"]
    recommendation = new_recommendation(
        Action.EXPEDITE if should_expedite else Action.MONITOR,
        expedite_units if should_expedite else Decimal("0"),
        tuple(reasons),
    )

    return Evaluation.new(
        case=case,
        policy=policy,
        projected_supply_units=projected_supply,
        coverage_ratio=coverage_ratio,
        shortfall_units=shortfall,
        shortfall_ratio=shortfall_ratio,
        scenarios=(no_action, expedite),
        recommendation=recommendation,
        assumptions=(
            "All inputs and calculations are synthetic reference assumptions, not validated planning policy.",
            "Unit margin is treated as recoverable contribution for the reference net-benefit calculation.",
            "Expedited units are assumed available up to max_expedite_units and are not written to a system of record.",
            "The recommendation cannot execute without a separately recorded human approval.",
        ),
    )
