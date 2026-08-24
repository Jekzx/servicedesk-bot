"""Core configuration and application settings."""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_database_url() -> str:
    """Return default database URL, handling Vercel/serverless /tmp environment."""
    env_db = os.getenv("DATABASE_URL")
    if env_db:
        return env_db
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return "sqlite:////tmp/servicedesk.db"
    return "sqlite:///./servicedesk.db"


class Settings(BaseSettings):
    APP_NAME: str = "ServiceDesk Bot & Diagnostics API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "production" if os.getenv("VERCEL") else "development"

    # Database Configuration (PostgreSQL / SQLite fallback with /tmp support for Vercel)
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

    # Security and CORS
    CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str = "super-secret-service-desk-bot-key-2026"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
