"""Pydantic schemas for Infrastructure and Monitored Services Health."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CorporateServiceSchema(BaseModel):
    id: str
    service_key: str
    name: str
    endpoint_url: str
    description: Optional[str] = None
    status: str  # OPERATIONAL, DEGRADED, OUTAGE, MAINTENANCE
    last_check: datetime
    latency_ms: float
    is_critical: bool

    model_config = ConfigDict(from_attributes=True)


class InfrastructureHealthResponse(BaseModel):
    system_status: str
    timestamp: datetime
    total_monitored: int
    operational_count: int
    degraded_count: int
    outage_count: int
    services: List[CorporateServiceSchema]


class ManualDiagnosticRequest(BaseModel):
    target: str  # e.g., "crm", "sap", "vpn", "ad", "dns", "gateway"
    phone_requester: Optional[str] = None


class DiagnosticCheckResult(BaseModel):
    target: str
    status: str
    is_operational: bool
    latency_ms: float
    message: str
    suggested_action: Optional[str] = None
