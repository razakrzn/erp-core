"""
Production settings.

This module imports base settings, explicitly loads values from `.env`,
and applies production-focused overrides.
"""

import os

from dotenv import load_dotenv

from .base import *  # noqa

# Explicitly load `.env` when running with config.settings.prod
# (environment variables already set by the OS/container are kept).
load_dotenv(BASE_DIR / ".env", override=False)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Production baseline
DEBUG = False

# DB fallback for docker-compose production (when DATABASE_URL is not used)
if not os.getenv("DATABASE_URL") and os.getenv("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": int(os.getenv("DB_PORT", "5432")),
            "OPTIONS": {
                "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
            },
            "DISABLE_SERVER_SIDE_CURSORS": True,
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        }
    }

db_sslmode = os.getenv("DB_SSLMODE", "").strip()
if db_sslmode and "default" in DATABASES:
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"]["sslmode"] = db_sslmode

# Reverse proxy / SSL
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = _env_bool("USE_X_FORWARDED_HOST", True)

# Cookies / transport
SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", True)
SESSION_COOKIE_HTTPONLY = _env_bool("SESSION_COOKIE_HTTPONLY", True)
CSRF_COOKIE_HTTPONLY = _env_bool("CSRF_COOKIE_HTTPONLY", True)
SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", True)

# Security headers
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
SECURE_HSTS_PRELOAD = _env_bool("SECURE_HSTS_PRELOAD", True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv(
    "SECURE_REFERRER_POLICY",
    "strict-origin-when-cross-origin",
)
X_FRAME_OPTIONS = os.getenv("X_FRAME_OPTIONS", "DENY")

# CSRF origins
raw_csrf_trusted_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in raw_csrf_trusted_origins.split(",")
    if origin.strip()
]

# Production logging default
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOGGING["root"]["level"] = LOG_LEVEL
