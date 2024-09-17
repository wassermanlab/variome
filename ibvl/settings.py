"""
Django settings for variome project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/

Quick-start development settings - unsuitable for production
See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
"""

import os
import dotenv
from pathlib import Path
import dj_database_url

dotenv.load_dotenv()

IS_DEVELOPMENT = os.environ.get("ENVIRONMENT") != "production"
DOMAIN = os.environ.get("HOST") or "127.0.0.1"
DB = os.environ.get("DB") or "postgresql://variome:variome@localhost:5432/variome"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    os.environ.get("DJANGO_SECRET_KEY")
    or "django-insecure-t=e420f^zm70rl(y%%wl6g!k97-od*b$i=y%qrq*z^r)_r-mc@"
)

AUTH_SERVER = os.environ.get("AUTH_SERVER", False)
AUTH_CLIENT_ID = os.environ.get("AUTH_CLIENT_ID", False)
AUTH_CLIENT_SECRET = os.environ.get("AUTH_CLIENT_SECRET", False)
AUTH_TENANT_ID = os.environ.get("AUTH_TENANT_ID", False)
AUTH_RELYING_PARTY_ID = os.environ.get("AUTH_RELYING_PARTY_ID", False)
AUTH_AUDIENCE = os.environ.get("AUTH_AUDIENCE", False)
AUTH_CA_BUNDLE = os.environ.get("AUTH_CA_BUNDLE", False)

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("TZ", False)
USE_I18N = True

admin_email = os.environ.get("ADMIN_EMAIL", False)
manager_email = os.environ.get("MANAGER_EMAIL", False)
#admins receive technical bug reports / stack traces
#ADMINS = [("Admin Name", "admin@example.com")]
if admin_email:
    ADMINS = [("Admin", admin_email)]

#managers are emailed alerts pertaining to data access limits (potential data abuse)
#MANAGERS = [("Manager Name", "manager@example.com")]
if manager_email:
    MANAGERS = [("Manager", manager_email)]

# internal alert emails
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[He Kākano] ")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "variome-admin-alerts-noreply@example.com")

EMAIL_HOST = os.environ.get("EMAIL_HOST", False)
EMAIL_PORT = os.environ.get("EMAIL_PORT", 25)
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", False)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", False)
EMAIL_SSL_CERTFILE = os.environ.get("EMAIL_SSL_CERTFILE", False)
EMAIL_SSL_KEYFILE = os.environ.get("EMAIL_SSL_KEYFILE", False)

if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    print(f"using smtp email backend at {EMAIL_HOST}")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    print("using console email backend")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = IS_DEVELOPMENT

ALLOWED_HOSTS = ["127.0.0.1", "localhost", DOMAIN]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    "pghistory.admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_extensions",
    "corsheaders",
    "tracking",
    "pghistory",
    "pgtrigger",
    "ibvl",
    "ibvl.library",
    "ibvl.library_access",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "tracking.middleware.VisitorTrackingMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "pghistory.middleware.HistoryMiddleware",
]
AUTHENTICATION_BACKENDS = []

if os.getenv("AUTH_AZUREAD", 'False').lower() == 'true':
    INSTALLED_APPS.append("django_auth_adfs")
    MIDDLEWARE.append("django_auth_adfs.middleware.LoginRequiredMiddleware")
    AUTHENTICATION_BACKENDS = [
        'django_auth_adfs.backend.AdfsAuthCodeBackend',
    ] + AUTHENTICATION_BACKENDS

    AUTH_ADFS = {
        "AUDIENCE": AUTH_CLIENT_ID,
        "CLIENT_ID": AUTH_CLIENT_ID,
        "CLIENT_SECRET": AUTH_CLIENT_SECRET,
        "GROUPS_CLAIM": "groups",
        "CLAIM_MAPPING": {
            "first_name": "given_name",
            "last_name": "family_name",
            "email": "upn",
        },
        "USERNAME_CLAIM": "upn",
        "GROUP_TO_FLAG_MAPPING": {
            "is_staff": [os.getenv("ADMINGROUP"), os.getenv("SUPERUSERGROUP")],
            "is_superuser": os.getenv("SUPERUSERGROUP"),
        },
        "TENANT_ID": AUTH_TENANT_ID,
        "RELYING_PARTY_ID": AUTH_CLIENT_ID,
        "LOGIN_EXEMPT_URLS": [
            "api/user",
            "accounts/login"
        ]
    }
    if AUTH_CA_BUNDLE:
        AUTH_ADFS["CA_BUNDLE"] = AUTH_CA_BUNDLE

    LOGIN_URL = "django_auth_adfs:login"
    LOGIN_REDIRECT_URL = f"/{os.getenv('URL_PREFIX')}admin/"

    CUSTOM_FAILED_RESPONSE_VIEW = 'ibvl.library_access.views.login_failed'

else:
    AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + [
        'django.contrib.auth.backends.ModelBackend'
    ]
    LOGIN_URL = "/"

TRACK_AJAX_REQUESTS = True
TRACK_PAGEVIEWS = True
TRACK_ANONYMOUS_USERS = False
TRACK_IGNORE_URLS = [
    "^(?!api\/variant\/).*$"
]  # ignore everything other than api/variant
TRACK_IGNORE_STATUS_CODES = [400, 404, 403, 405, 410, 429, 500]

ROOT_URLCONF = "ibvl.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["ibvl/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "ibvl.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {"default": dj_database_url.parse(DB)}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3123",
    "http://" + DOMAIN,
    "https://" + DOMAIN,
    "http://" + DOMAIN + ":3000",
    "https://" + DOMAIN + ":3000",
    "http://" + DOMAIN + ":8000",
    "https://" + DOMAIN + ":8000",
]


# for the "View Site" link in admin dashboard toolbar
if isinstance(os.environ.get("FRONTEND_URL"), str):
    SITE_URL = os.environ.get("FRONTEND_URL")
else:
    SITE_URL = "https://" + DOMAIN
    

# Authentication
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
#        "loggers": {
#            "django.db.backends": {
#                "handlers": ["console"],
#                "level": "DEBUG",
#            },
#        },
    }
else:
    LOGGING = {}
