from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import AnyHttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────
    APP_NAME: str = "EduCore School Management Platform"
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    API_PREFIX: str = "/api/v1"
    APP_VERSION: str = "2.0.0"

    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.ALLOWED_ORIGINS.split(",") if x.strip()]

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_DB: int = 1
    REDIS_QUEUE_DB: int = 2
    REDIS_RESULT_DB: int = 3

    # ── JWT ───────────────────────────────────────────────────

    @field_validator('DATABASE_URL')
    @classmethod
    def fix_database_url_protocol(cls, v: str) -> str:
        if v.startswith('postgres://'):
            return v.replace('postgres://', 'postgresql+asyncpg://', 1)
        if v.startswith('postgresql://') and 'asyncpg' not in v:
            return v.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return v


    @field_validator('REDIS_URL')
    @classmethod
    def fix_redis_url_protocol(cls, v: str) -> str:
        # Some providers give redis://:password@host:port
        # async-redis is fine with this usually, but let's ensure it starts correctly
        if v.startswith('redis://') or v.startswith('rediss://'):
            return v
        return f'redis://{v}'

    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_RESET_TOKEN_EXPIRE_HOURS: int = 2
    JWT_VERIFY_TOKEN_EXPIRE_HOURS: int = 24

    # ── Celery ────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/3"

    # ── File Storage (Cloudflare R2) ──────────────────────────
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "educore-files"
    R2_PUBLIC_URL: str = "http://localhost:9000/educore-files"
    R2_REGION: str = "auto"

    # ── Email ─────────────────────────────────────────────────
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@educore.in"
    EMAIL_FROM_NAME: str = "EduCore"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_TLS: bool = False
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # ── SMS (MSG91) ───────────────────────────────────────────
    MSG91_AUTH_KEY: str = ""
    MSG91_SENDER_ID: str = "EDCORE"
    MSG91_TEMPLATE_ID_OTP: str = ""
    MSG91_TEMPLATE_ID_ABSENCE: str = ""
    MSG91_TEMPLATE_ID_FEE: str = ""

    # ── Payment (Razorpay) ────────────────────────────────────
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # ── Monitoring ────────────────────────────────────────────
    SENTRY_DSN: str = ""

    # ── Encryption ────────────────────────────────────────────
    PII_ENCRYPTION_KEY: str = ""

    # ── Firebase (Push Notifications) ────────────────────────
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""

    # ── Feature Flags ─────────────────────────────────────────
    FEATURE_WHATSAPP_ENABLED: bool = False
    FEATURE_AI_ANALYTICS: bool = False
    FEATURE_MULTI_SCHOOL: bool = True
    FEATURE_LIBRARY_MODULE: bool = False
    FEATURE_BUS_TRACKING: bool = False

    # ── Limits & Thresholds ───────────────────────────────────
    MAX_FILE_UPLOAD_MB: int = 10
    MAX_BULK_IMPORT_ROWS: int = 2000
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_API_PER_MINUTE: int = 200
    MIN_ATTENDANCE_PERCENTAGE: int = 75
    DEFAULT_LATE_FEE_PER_DAY: int = 10

    # ── TOTP / 2FA ────────────────────────────────────────────
    TOTP_ISSUER_NAME: str = "EduCore"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @field_validator("PII_ENCRYPTION_KEY")
    @classmethod
    def pii_encryption_key_must_be_valid(cls, v: str) -> str:
        if not v:
            return v  # Allow empty in dev if needed, logic in encryption.py handles it
        try:
            from cryptography.fernet import Fernet
            Fernet(v.encode())
        except Exception:
            raise ValueError("PII_ENCRYPTION_KEY must be a valid Fernet key (base64-encoded 32 bytes)")
        return v



    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_FILE_UPLOAD_MB * 1024 * 1024

    @property
    def redis_cache_url(self) -> str:
        base = self.REDIS_URL.rsplit("/", 1)[0]
        return f"{base}/{self.REDIS_CACHE_DB}"

    @property
    def r2_endpoint_url(self) -> str:
        if not self.R2_ACCOUNT_ID:
            return "http://localhost:9000"  # Default for MinIO/Local dev
        return f"https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
