import os
from decouple import config as decouple_config, Csv, Config, RepositoryEnv
from datetime import timedelta
from corsheaders.defaults import default_headers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, "apps", ".env")
config = Config(RepositoryEnv(ENV_FILE)) if os.path.exists(ENV_FILE) else decouple_config
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def cast_debug(value):
    normalized = str(value).strip().lower()
    if normalized in {"release", "prod", "production"}:
        return False
    if normalized in {"debug", "dev", "development"}:
        return True
    return bool(value) if normalized == "" else normalized in {"1", "true", "t", "yes", "y", "on"}


SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-change-me-in-production"
)

DEBUG = config("DEBUG", default=True, cast=cast_debug)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,.localhost,acme.localhost",
    cast=Csv(),
)

# ──────────────────────────────────────────────
# django-tenants configuration
# ──────────────────────────────────────────────

SHARED_APPS = [
    "django_tenants",

    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "guardian",
    "apps.core",
    "apps.subscriptions",
    "apps.accounts",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_celery_beat",
    "django_celery_results", 
]

TENANT_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "guardian",
    "apps.accounts",
    "apps.employees",
    "apps.leave",
    "apps.attendance",
    "apps.biometric",
    "apps.security",
]


INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS
    if app not in SHARED_APPS
]

TENANT_MODEL = "core.Tenant"
TENANT_DOMAIN_MODEL = "core.Domain"

ROOT_URLCONF = "config.urls"
PUBLIC_SCHEMA_URLCONF = "config.urls_public"

# ──────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────

MIDDLEWARE = [
    "apps.core.middleware.CustomTenantMiddleware",

    "django.middleware.security.SecurityMiddleware",

    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]



TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [os.path.join(BASE_DIR, "templates")],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ──────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": config("DATABASE_NAME", default="hrms_db"),
        "USER": config("DATABASE_USER", default="postgres"),
        "PASSWORD": config("DATABASE_PASSWORD", default="admin@123"),
        "HOST": config("DATABASE_HOST", default="localhost"),
        "PORT": config("DATABASE_PORT", default="5432"),
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }
}

DATABASE_ROUTERS = (
    "django_tenants.routers.TenantSyncRouter",
)

# ──────────────────────────────────────────────
# Authentication
# ──────────────────────────────────────────────

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",

        "OPTIONS": {
            "min_length": 8
        },
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# ──────────────────────────────────────────────
# JWT
# ──────────────────────────────────────────────

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=180),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),

    "ROTATE_REFRESH_TOKENS": True,

    "BLACKLIST_AFTER_ROTATION": True,

    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",

    "SIGNING_KEY": SECRET_KEY,

    "AUTH_HEADER_TYPES": ("Bearer",),

    "USER_ID_FIELD": "id",

    "USER_ID_CLAIM": "user_id",

    "TOKEN_OBTAIN_SERIALIZER":
        "apps.core.serializers.TenantTokenObtainPairSerializer",
}

# ──────────────────────────────────────────────
# Django REST Framework
# ──────────────────────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # 'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardCursorPagination',
    # 'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'apps.core.renderers.ApiRenderer',
    # ),
    'DEFAULT_SCHEMA_CLASS': 'apps.core.schema.HRMSAutoSchema',
    # 'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}


# ──────────────────────────────────────────────
# CORS
# ──────────────────────────────────────────────

CORS_ALLOW_ALL_ORIGINS = DEBUG

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default=(
        "http://localhost:5173",
        "http://localhost:3000",
        "http://acme.localhost:5173",
        "http://acme.localhost:3000",
        "https://hrms.yourcompany.com"
    ),
    cast=Csv(),
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-tenant-schema",
]

CORS_EXPOSE_HEADERS = [
    "Content-Type",
    "X-CSRFToken",
]

# ──────────────────────────────────────────────
# Celery
# ──────────────────────────────────────────────

CELERY_BROKER_URL = config(
    "CELERY_BROKER_URL",
    default="redis://localhost:6379/1"
)

CELERY_RESULT_BACKEND = "django-db"

CELERY_CACHE_BACKEND = "django-cache"

CELERY_ACCEPT_CONTENT = ["json"]

CELERY_TASK_SERIALIZER = "json"

CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = "UTC"

CELERY_BEAT_SCHEDULER = (
    "django_celery_beat.schedulers:DatabaseScheduler"
)

# ──────────────────────────────────────────────
# Cache
# ──────────────────────────────────────────────

if config("CACHE_BACKEND", default="locmem").lower() == "redis":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": config("REDIS_URL", default="redis://localhost:6379/0"),
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "hrms-local-cache",
        }
    }

# ──────────────────────────────────────────────
# Static & Media
# ──────────────────────────────────────────────

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"

MEDIA_ROOT = config(
    "MEDIA_ROOT",
    default=os.path.join(BASE_DIR, "media")
)

# ──────────────────────────────────────────────
# ESS Document Storage
# ──────────────────────────────────────────────

ESS_DOCUMENT_STORAGE = {
    "BACKEND": config(
        "ESS_STORAGE_BACKEND",
        default="local"
    ),

    "LOCAL_MEDIA_ROOT": MEDIA_ROOT,

    "S3_BUCKET": config(
        "ESS_S3_BUCKET",
        default=""
    ),

    "S3_PREFIX": "hrms/employees/",

    "SIGNED_URL_TTL": 3600,
}

# ──────────────────────────────────────────────
# Storage Backend
# ──────────────────────────────────────────────

STORAGE_BACKEND = config(
    "STORAGE_BACKEND",
    default="apps.core.storage.local.LocalStorageBackend"
)

MAX_UPLOAD_SIZE_MB = config(
    "MAX_UPLOAD_SIZE_MB",
    default=10,
    cast=int
)

# ──────────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────────

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ──────────────────────────────────────────────
# DRF Spectacular
# ──────────────────────────────────────────────

SPECTACULAR_SETTINGS = {
    "TITLE": "HRMS Employee Self-Service API",

    "DESCRIPTION": (
        "Enterprise-grade multi-tenant HRMS ESS API"
    ),

    "VERSION": "1.0.0",

    "SERVE_INCLUDE_SCHEMA": False,

    "COMPONENT_SPLIT_REQUEST": True,

    "SCHEMA_PATH_PREFIX": r"/api/",

    "SECURITY": [{"BearerAuth": []}],

    "SWAGGER_UI_DIST": "SIDECAR",

    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",

    "REDOC_DIST": "SIDECAR",

    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
}

# ──────────────────────────────────────────────
# ESS Feature Flags
# ──────────────────────────────────────────────

ESS_CONFIG = {
    "ALLOW_EMPLOYEE_CANCEL_REQUEST": True,

    "MAX_PENDING_PER_MODULE": 3,

    "EMAIL_NOTIFY_HR_ON_NEW_REQUEST": True,

    "HR_NOTIFICATION_EMAIL": config(
        "HR_NOTIFICATION_EMAIL",
        default="hr@company.com"
    ),

    "EMAIL_NOTIFY_EMPLOYEE_ON_DECISION": True,

    "PASSPORT_EXPIRY_WARNING_DAYS": 90,

    "CERT_EXPIRY_WARNING_DAYS": 60,
    "TAGS": [
        {"name": "Employee (Leave)", "description": "Leave APIs for employees."},
        {"name": "Admin (Leave)", "description": "Leave APIs for admin users."},
        {"name": "Manager (Leave)", "description": "Leave APIs for managers."},
    ],
}

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────

LOGGING = {
    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format":
                "[{asctime}] {levelname} "
                "{name} {process:d} {thread:d} {message}",

            "style": "{",
        },

        "simple": {
            "format":
                "[{asctime}] {levelname} {name}: {message}",

            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",

            "formatter": "simple",
        },

        "ess_file": {
            "class":
                "logging.handlers.RotatingFileHandler",

            "filename": os.path.join(LOG_DIR, "ess.log"),

            "maxBytes": 10 * 1024 * 1024,

            "backupCount": 5,

            "formatter": "verbose",
        },

        "audit_file": {
            "class":
                "logging.handlers.RotatingFileHandler",

            "filename": os.path.join(LOG_DIR, "ess_audit.log"),

            "maxBytes": 20 * 1024 * 1024,

            "backupCount": 10,

            "formatter": "verbose",
        },
    },

    "root": {
        "handlers": ["console"],

        "level": "INFO",
    },

    "loggers": {
        "apps.employees": {
            "handlers": [
                "console",
                "ess_file"
            ],

            "level": "INFO",

            "propagate": False,
        },

        "apps.employees.audit": {
            "handlers": [
                "audit_file"
            ],

            "level": "INFO",

            "propagate": False,
        },

        "django.request": {
            "handlers": ["console"],

            "level": "WARNING",

            "propagate": False,
        },

        "django.db.backends": {
            "level": "WARNING",

            "handlers": ["console"],

            "propagate": False,
        },
    },
}


AGENT_API_KEY = config("ESSL_AGENT_API_KEY",default="hfjhghchgjh")


import tempfile

IMPORT_TEMP_DIR = tempfile.gettempdir()

LOCAL_TENANT_SCHEMA = config("LOCAL_TENANT_SCHEMA", default="acme")