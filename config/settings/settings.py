"""
Django settings for config project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def get_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return value


def env_bool(name: str) -> bool:
    return get_env(name).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str) -> list[str]:
    value = get_env(name)
    return [item.strip() for item in value.split(",") if item.strip()]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env("SECRET_KEY")

# SECURITY WARNING: keep disabled on deployed environments.
DEBUG = env_bool("DEBUG")

# CORS
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS")
CORS_ORIGIN_ALLOW_ALL = CORS_ALLOW_ALL_ORIGINS  # Backward compatibility (older django-cors-headers).
if CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = []
else:
    CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS  # Backward compatibility (older django-cors-headers).
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
APPEND_SLASH = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

FORCE_SCRIPT_NAME = '/'

USE_X_FORWARDED_HOST = True

# Coolify test mode: serve uploaded media through Django URLs even with DEBUG=False.
# Keep this True only while no dedicated reverse-proxy/static server is configured.
SERVE_MEDIA_WITH_DJANGO = env_bool("SERVE_MEDIA_WITH_DJANGO")


# Application definition

INSTALLED_APPS = [
    "apps.accounts",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "django_redis",
    # Domain apps (under the `apps` package)
    "apps.company",
    "apps.navigation",
    "apps.access_control",
    "apps.rbac",
    "apps.hrm",
    "apps.crm.apps.CrmConfig",
    "apps.Projects.apps.ProjectsConfig",
    "apps.inventory",
    "apps.production",
    "apps.assessment.apps.AssessmentConfig",
    "apps.settings.apps.SettingsConfig",
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
    "DEFAULT_PERMISSION_CLASSES": ["core.permissions.rbac_permission.RBACPermission"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": get_env("DB_NAME"),
        "USER": get_env("DB_USER"),
        "PASSWORD": get_env("DB_PASSWORD"),
        "HOST": get_env("DB_HOST"),
        "PORT": int(get_env("DB_PORT")),
        "OPTIONS": {
            "connect_timeout": int(get_env("DB_CONNECT_TIMEOUT")),
        },
        "CONN_MAX_AGE": int(get_env("DB_CONN_MAX_AGE")),
    }
}


# Caching
# https://docs.djangoproject.com/en/6.0/topics/cache/

redis_url = get_env("REDIS_CACHE_URL")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": redis_url,
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

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_MANIFEST_FILE = STATIC_ROOT / "staticfiles.json"

_staticfiles_backend = "whitenoise.storage.CompressedManifestStaticFilesStorage"
if not STATICFILES_MANIFEST_FILE.exists():
    _staticfiles_backend = "whitenoise.storage.CompressedStaticFilesStorage"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": _staticfiles_backend},
}
MEDIA_URL = "/media/"

# Persist uploads outside app code path on server.
# Fallback to repo-local media path when /var/www is not writable (e.g. local macOS dev).
_preferred_media_root = Path("/var/www/media")
_fallback_media_root = BASE_DIR / "media"
try:
    _preferred_media_root.mkdir(parents=True, exist_ok=True)
    MEDIA_ROOT = _preferred_media_root
except (PermissionError, OSError):
    _fallback_media_root.mkdir(parents=True, exist_ok=True)
    MEDIA_ROOT = _fallback_media_root

# Celery / background jobs
CELERY_BROKER_URL = get_env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = get_env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

AUTH_USER_MODEL = "accounts.User"


# Logging
# Hardcoded log level for test.
LOG_LEVEL = get_env("LOG_LEVEL")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        # Keep explicit module logger to ensure BOQ debug traces are visible.
        "api.v1.assessment": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}
