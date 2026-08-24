"""Core configuration and application settings."""
import os
from typing import List, Union, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Clean empty strings from environment variables so pydantic-settings doesn't fail on complex types
for k in list(os.environ.keys()):
    if os.environ.get(k) == "":
        del os.environ[k]


def get_default_database_url() -> str:
    """Return default database URL, handling Vercel/serverless /tmp environment."""
    env_db = os.getenv("DATABASE_URL")
    if env_db and env_db.strip():
        if env_db.startswith("postgres://"):
            return env_db.replace("postgres://", "postgresql://", 1)
        return env_db.strip()
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return "sqlite:////tmp/servicedesk.db"
    return "sqlite:///./servicedesk.db"


class Settings(BaseSettings):
    APP_NAME: str = "ServiceDesk Bot & Diagnostics API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "production" if os.getenv("VERCEL") else "development"

    # Database Configuration
    DATABASE_URL: str = get_default_database_url()

    # Meta WhatsApp Cloud API Settings
    WHATSAPP_VERIFY_TOKEN: str = "SERVICE_DESK_WEBHOOK_VERIFY_TOKEN_2026"
    WHATSAPP_API_TOKEN: str = "EAAG...MOCK_TOKEN"
    WHATSAPP_PHONE_NUMBER_ID: str = "10987654321"
    WHATSAPP_API_VERSION: str = "v19.0"

    # Corporate Monitored Infrastructure Endpoints
    CRM_URL: str = "https://crm.internal.corp"
    ERP_SAP_URL: str = "https://sap.internal.corp"
    VPN_GATEWAY_URL: str = "https://vpn.internal.corp"
    AUTH_AD_URL: str = "https://auth.internal.corp"
    DATABASE_PROD_HOST: str = "db-prod.internal.corp"

    # Security and CORS (Using string to avoid JSONDecodeError on empty env variables)
    CORS_ORIGINS_RAW: Union[str, List[str]] = "*"
    SECRET_KEY: str = "super-secret-service-desk-bot-key-2026"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS_RAW, list):
            return self.CORS_ORIGINS_RAW
        if isinstance(self.CORS_ORIGINS_RAW, str):
            if self.CORS_ORIGINS_RAW.strip() in ("", "*"):
                return ["*"]
            return [x.strip() for x in self.CORS_ORIGINS_RAW.split(",") if x.strip()]
        return ["*"]

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_leniently(cls, v: Any) -> bool:
        if v is None or v == "":
            return False
        if isinstance(v, str):
            return v.strip().lower() in ("true", "1", "t", "yes", "y", "on")
        return bool(v)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def parse_database_url(cls, v: Any) -> str:
        if not v or not str(v).strip():
            return get_default_database_url()
        val_str = str(v).strip()
        if val_str.startswith("postgres://"):
            return val_str.replace("postgres://", "postgresql://", 1)
        return val_str


settings = Settings()
