"""Healthcheck and Corporate Infrastructure Diagnostics router."""
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import (
    InfrastructureHealthResponse,
    CorporateServiceSchema,
    ManualDiagnosticRequest,
    DiagnosticCheckResult,
)
from app.services.auto_fix import auto_fix_service

router = APIRouter(prefix="/api/health", tags=["Health & Diagnostics"])


@router.get("", summary="API Basic Healthcheck")
def basic_health():
    """Basic healthcheck to verify API server liveness."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


@router.get("/services", response_model=InfrastructureHealthResponse, summary="Corporate Monitored Services Status")
async def monitored_services_health(db: Session = Depends(get_db)):
    """
    Returns real-time operational status, latency, and outage reports
    for all monitored corporate services (CRM, ERP SAP, VPN, AD, DB).
    """
    services = await auto_fix_service.get_all_services_health(db)
    
    operational_count = sum(1 for s in services if s.status == "OPERATIONAL")
    degraded_count = sum(1 for s in services if s.status == "DEGRADED")
    outage_count = sum(1 for s in services if s.status == "OUTAGE")

    overall_status = "ALL_SYSTEMS_OPERATIONAL"
    if outage_count > 0:
        overall_status = "MAJOR_OUTAGE"
    elif degraded_count > 0:
        overall_status = "PARTIAL_DEGRADATION"

    return InfrastructureHealthResponse(
        system_status=overall_status,
        timestamp=datetime.datetime.utcnow(),
        total_monitored=len(services),
        operational_count=operational_count,
        degraded_count=degraded_count,
        outage_count=outage_count,
        services=[CorporateServiceSchema.model_validate(s) for s in services]
    )


@router.post("/diagnostics", response_model=DiagnosticCheckResult, summary="Run Active Diagnostic Check on Service")
async def run_diagnostic(
    payload: ManualDiagnosticRequest,
    db: Session = Depends(get_db)
):
    """Trigger on-demand diagnostics for a specific service target."""
    result = await auto_fix_service.run_diagnostics_for_key(payload.target, db)
    
    return DiagnosticCheckResult(
        target=payload.target,
        status=result["status"],
        is_operational=result["is_operational"],
        latency_ms=result["latency_ms"],
        message=result["message"],
        suggested_action="Nenhuma ação necessária" if result["is_operational"] else "Verifique logs do cluster ou reinicie o gateway."
    )
