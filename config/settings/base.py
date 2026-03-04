"""
Base Django settings for config project.

This module was split out from the original `config/settings.py` to support
environment-specific settings modules such as `dev` and `prod`.
"""

from pathlib import Path
import os
from urllib.parse import urlparse

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env (useful for local dev; in Docker they
# are also provided via the env file configured in docker-compose).
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-23cn5avp2f!&88oio-5e$a90d^h!-8)uo@4$e^3@j@da0i0&_m",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

raw_allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [
    host.strip()
    for host in raw_allowed_hosts.split(",")
    if host.strip()
]

# CORS: from .env — use "*" to allow all origins, or comma-separated list
_raw_cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
if _raw_cors_origins.upper() == "*" or _raw_cors_origins.lower() == "true":
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in _raw_cors_origins.split(",")
        if origin.strip()
    ]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
    "django_redis",
    # Domain apps (under the `apps` package)
    "apps.accounts",
    "apps.company",
    "apps.navigation",
    "apps.access_control",
    "apps.rbac",
    "apps.hrm",
    "apps.inventory",
    "apps.production",
]

REST_FRAMEWORK = {
    # Use the custom pagination by default
    "DEFAULT_PAGINATION_CLASS": "core.utils.pagination.IndustrialPagination",
    # Global exception handler
    "EXCEPTION_HANDLER": "core.utils.responses.custom_exception_handler",
    # Use standard JSON rendering
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    # Authentication: use JWT by default (plus session for browsable API)
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "core.permissions.rbac_permission.RBACPermission"
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# OpenAPI schema (drf-spectacular)
SPECTACULAR_SETTINGS = {
    "TITLE": "ERP Core API",
    "DESCRIPTION": (
        "REST API for ERP Core: companies, accounts, auth (JWT), HRM (employees, departments, "
        "designations, attendance), inventory, production (orders, cutting, BOM, etc.), "
        "navigation, access control, and RBAC. Use JWT access tokens in the Authorization header."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": "Auth", "description": "Login and JWT token refresh."},
        {"name": "Company", "description": "Company CRUD and settings."},
        {"name": "Accounts", "description": "User accounts and check-username."},
        {"name": "Navigation", "description": "Modules, features, permissions, sidebar."},
        {"name": "Access control", "description": "API access and permissions."},
        {"name": "HRM", "description": "Departments, designations, employees, attendance."},
        {"name": "Inventory", "description": "Products, materials, categories, brands, sizes."},
        {"name": "Production", "description": "Orders, cutting optimization, BOM, labor, etc."},
        {"name": "RBAC", "description": "Role-based access control."},
    ],
    "TAGS_ORDER": [
        "Auth",
        "Company",
        "Accounts",
        "Navigation",
        "Access control",
        "HRM",
        "Inventory",
        "Production",
        "RBAC",
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "config.middleware.company_context.CompanyContextMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.tenant_middleware.TenantMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

database_url = os.getenv("DATABASE_URL")

if database_url:
    parsed_url = urlparse(database_url)

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed_url.path.lstrip("/") or None,
            "USER": parsed_url.username,
            "PASSWORD": parsed_url.password,
            "HOST": parsed_url.hostname,
            "PORT": parsed_url.port or 5432,
        }
    }
else:
    # Fallback to local SQLite for development if no DATABASE_URL is provided.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Caching
# https://docs.djangoproject.com/en/6.0/topics/cache/

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Celery / background jobs
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"))
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

AUTH_USER_MODEL = "accounts.User"
