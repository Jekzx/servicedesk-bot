"""Corporate User, Department, and Monitored Service Models."""
import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class CorporateUser(Base, TimestampMixin):
    __tablename__ = "corporate_users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    phone = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    department = Column(String(50), default="Operações", nullable=False)
    role = Column(String(50), default="Colaborador", nullable=False)
    is_vip = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<CorporateUser {self.name} ({self.department})>"


class CorporateService(Base):
    __tablename__ = "corporate_services"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    service_key = Column(String(50), unique=True, index=True, nullable=False)  # crm, sap, vpn, ad, database
    name = Column(String(100), nullable=False)
    endpoint_url = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(String(20), default="OPERATIONAL", nullable=False)  # OPERATIONAL, DEGRADED, OUTAGE, MAINTENANCE
    last_check = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    latency_ms = Column(Float, default=0.0, nullable=False)
    is_critical = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<CorporateService {self.name}: {self.status}>"
