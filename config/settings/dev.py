"""
Settings for the Render development server.

Used when DJANGO_SETTINGS_MODULE=config.settings.dev (set in Render env).
Imports base then overrides for the deployed Render environment.
"""

import dj_database_url
from .base import *  # noqa

# Render: use DATABASE_URL (required; set by Render when linking PostgreSQL)
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the environment on Render.")
DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600),
}

# Render: DEBUG off by default (set DEBUG=True in Render env if needed)
DEBUG = os.getenv("DEBUG", "False") == "True"

# Render: allow *.onrender.com; env ALLOWED_HOSTS can add more (comma-separated)
_raw = os.getenv("ALLOWED_HOSTS", ".onrender.com").strip()
ALLOWED_HOSTS = [h.strip() for h in _raw.split(",") if h.strip()]
if ".onrender.com" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(".onrender.com")

# Render: no Redis by default; use DummyCache unless REDIS_URL is set
_redis_url = os.getenv("REDIS_URL", "").strip()
if _redis_url and (_redis_url.startswith("redis://") or _redis_url.startswith("rediss://")):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

# SECRET_KEY must be set in Render env (no insecure default)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY must be set in the environment on Render (e.g. via Render Dashboard or render.yaml)"
    )
