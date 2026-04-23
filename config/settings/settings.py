"""
Django settings for config project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-23cn5avp2f!&88oio-5e$a90d^h!-8)uo@4$e^3@j@da0i0&_m"

# SECURITY WARNING: keep disabled on deployed environments.
DEBUG = False

# CORS: hardcoded values only for test.
DEFAULT_CORS_ORIGINS = [
    "https://erp.emeraldinterior.com",
]

# TEMP TEST MODE: allow every origin to verify whether failures are CORS-policy related.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = CORS_ALLOW_ALL_ORIGINS  # Backward compatibility (older django-cors-headers).
CORS_ALLOWED_ORIGINS = DEFAULT_CORS_ORIGINS
CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS  # Backward compatibility (older django-cors-headers).
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    "http://erp.emeraldinterior.com",
    "https://erp.emeraldinterior.com"
]
APPEND_SLASH = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

FORCE_SCRIPT_NAME = '/'

USE_X_FORWARDED_HOST = True

# Coolify test mode: serve uploaded media through Django URLs even with DEBUG=False.
# Keep this True only while no dedicated reverse-proxy/static server is configured.
SERVE_MEDIA_WITH_DJANGO = True


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
        "NAME": "emrdb",
        "USER": "root",
        "PASSWORD": "zF2XKic8xBOiRAjA482g12LfHZyiDSpon1MSyNfWGznKNzI290OWkNnAG0D6YgBT",
        "HOST": "72.62.254.95",
        "PORT": 3307,
        "OPTIONS": {
            "connect_timeout": 10,
        },
        "CONN_MAX_AGE": 60,
    }
}


# Caching
# https://docs.djangoproject.com/en/6.0/topics/cache/

redis_url = "redis://127.0.0.1:6379/1"

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

# Keep media storage deterministic across restarts.
# Override with MEDIA_ROOT=/absolute/path in environment when needed.
# Local development defaults to repo media directory to avoid permission issues.
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT") or (BASE_DIR / "media"))
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Celery / background jobs
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

AUTH_USER_MODEL = "accounts.User"


# Logging
# Hardcoded log level for test.
LOG_LEVEL = "DEBUG"

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
