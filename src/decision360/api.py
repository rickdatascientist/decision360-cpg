"""Authenticated FastAPI surface for the Decision360 reference beta."""

import os
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .auth import ApiKeyAuth, Principal
from .engine import DecisionInputError, evaluate_case
from .models import DecisionCase, Policy
from .store import SQLiteStore, StoreConflict, StoreNotFound
from .tools import DecisionTools


class EvidenceInput(BaseModel):
    field: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=500)
    observed_at: str = Field(min_length=1, max_length=100)
    note: str = Field(default="", max_length=1000)


class PolicyInput(BaseModel):
    min_shortfall_ratio: Decimal = Field(default=Decimal("0.05"), ge=0)
    min_net_benefit: Decimal = Field(default=Decimal("0"), ge=0)
    allow_expedite: bool = True


class EvaluationInput(BaseModel):
    case_id: str = Field(min_length=1, max_length=100)
    sku: str = Field(min_length=1, max_length=100)
    period: str = Field(min_length=1, max_length=100)
    forecast_units: Decimal = Field(ge=0)
    available_inventory_units: Decimal = Field(ge=0)
    confirmed_inbound_units: Decimal = Field(ge=0)
    unit_margin: Decimal = Field(ge=0)
    expedite_unit_cost: Decimal = Field(ge=0)
    max_expedite_units: Decimal = Field(ge=0)
    evidence: list[EvidenceInput] = Field(min_length=1, max_length=50)
    policy: PolicyInput = Field(default_factory=PolicyInput)


class ApprovalInput(BaseModel):
    decision: Literal["approved", "rejected"]
    rationale: str = Field(min_length=1, max_length=2000)


class OutcomeInput(BaseModel):
    actual_recovered_units: Decimal = Field(ge=0)
    realized_net_value: Decimal
    note: str = Field(default="", max_length=2000)


class ToolInput(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


def create_app(
    *,
    database_path: str | Path | None = None,
    auth: ApiKeyAuth | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Decision360 CPG Reference API",
        version="0.2.0",
        description="Synthetic reference beta. No autonomous execution or validated planning claims.",
    )
    app.state.store = SQLiteStore(database_path or os.getenv("DECISION360_DB", "var/decision360.db"))
    app.state.auth = auth or ApiKeyAuth.from_environment()
    app.state.tools = DecisionTools(app.state.store)

    def require_roles(*allowed: str):
        def dependency(request: Request, x_api_key: Annotated[str | None, Header()] = None) -> Principal:
            manager: ApiKeyAuth = request.app.state.auth
            if not manager.keys:
                raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "API authentication is not configured")
            principal = manager.authenticate(x_api_key)
            if principal is None:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid API key")
            if "admin" not in principal.roles and not principal.roles.intersection(allowed):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Role is not authorized for this operation")
            return principal

        return dependency

    @app.get("/healthz")
    def health(request: Request) -> dict[str, Any]:
        store: SQLiteStore = request.app.state.store
        return {"status": "ok", "audit_integrity": store.verify_audit_integrity()}

    @app.post("/api/v1/evaluations")
    def create_evaluation(
        body: EvaluationInput,
        response: Response,
        request: Request,
        principal: Annotated[Principal, Depends(require_roles("operator"))],
        idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=200)],
    ) -> dict[str, Any]:
        payload = body.model_dump(mode="json")
        try:
            evaluation = evaluate_case(DecisionCase.from_dict(payload), Policy.from_dict(payload.get("policy")))
            stored, replayed = request.app.state.store.save_evaluation(
                evaluation,
                idempotency_key=idempotency_key,
                request_hash=SQLiteStore.request_hash(payload),
                actor=principal.actor,
            )
        except DecisionInputError as error:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
        except StoreConflict as error:
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
        response.status_code = status.HTTP_200_OK if replayed else status.HTTP_201_CREATED
        return {"replayed": replayed, "evaluation": stored}

    @app.get("/api/v1/evaluations/{evaluation_id}")
    def get_evaluation(
        evaluation_id: str,
        request: Request,
        _: Annotated[Principal, Depends(require_roles("viewer", "operator", "approver", "auditor"))],
    ) -> dict[str, Any]:
        try:
            return {"evaluation": request.app.state.store.get_evaluation(evaluation_id)}
        except StoreNotFound as error:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    @app.post("/api/v1/recommendations/{recommendation_id}/approval", status_code=201)
    def approve(
        recommendation_id: str,
        body: ApprovalInput,
        request: Request,
        principal: Annotated[Principal, Depends(require_roles("approver"))],
    ) -> dict[str, Any]:
        try:
            approval = request.app.state.store.record_approval(
                recommendation_id,
                decision=body.decision,
                actor=principal.actor,
                rationale=body.rationale,
            )
        except StoreNotFound as error:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
        except StoreConflict as error:
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
        return {"approval": approval}

    @app.post("/api/v1/recommendations/{recommendation_id}/outcomes")
    def outcome(
        recommendation_id: str,
        body: OutcomeInput,
        response: Response,
        request: Request,
        principal: Annotated[Principal, Depends(require_roles("operator"))],
        idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=200)],
    ) -> dict[str, Any]:
        payload = body.model_dump(mode="json")
        try:
            stored, replayed = request.app.state.store.record_outcome(
                recommendation_id,
                idempotency_key=idempotency_key,
                request_hash=SQLiteStore.request_hash({"recommendation_id": recommendation_id, **payload}),
                actual_recovered_units=str(body.actual_recovered_units),
                realized_net_value=str(body.realized_net_value),
                actor=principal.actor,
                note=body.note,
            )
        except StoreConflict as error:
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
        response.status_code = status.HTTP_200_OK if replayed else status.HTTP_201_CREATED
        return {"replayed": replayed, "outcome": stored}

    @app.get("/api/v1/audit/integrity")
    def audit_integrity(
        request: Request,
        _: Annotated[Principal, Depends(require_roles("auditor"))],
    ) -> dict[str, Any]:
        store: SQLiteStore = request.app.state.store
        events = store.audit_events()
        return {"valid": store.verify_audit_integrity(), "event_count": len(events)}

    @app.post("/api/v1/tools/{tool_name}")
    def tool_call(
        tool_name: str,
        body: ToolInput,
        request: Request,
        principal: Annotated[Principal, Depends(require_roles("viewer", "operator", "approver", "auditor"))],
    ) -> dict[str, Any]:
        return request.app.state.tools.execute(tool_name, body.arguments, principal)

    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        "decision360.api:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )


if __name__ == "__main__":
    run()
