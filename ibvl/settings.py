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


is_development = os.environ.get("ENVIRONMENT") != "production"
DOMAIN = os.environ.get("HOST") or '127.0.0.1'
DB = os.environ.get("DB") or "postgresql://variome:variome@localhost:5432/variome"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or 'django-insecure-t=e420f^zm70rl(y%%wl6g!k97-od*b$i=y%qrq*z^r)_r-mc@' 

is_development = os.environ.get("ENVIRONMENT") != "production"

LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.environ.get('TZ') or 'America/Vancouver'
USE_I18N = True
USE_TZ = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = is_development

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    DOMAIN
]


# Application definition

INSTALLED_APPS = [
    'ibvl.apps.IbvlConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.saml',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_extensions',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'ibvl.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]
SOCIALACCOUNT_PROVIDERS = {
    "saml": {
        # Here, each app represents the SAML provider configuration of one
        # organization.
        "APPS": [
            {
                # Used for display purposes, e.g. over by: {% get_providers %}
                "name": "Acme Inc",

                # Accounts signed up via this provider will have their
                # `SocialAccount.provider` value set to this ID. The combination
                # of this value and the `uid` must be unique. The IdP entity ID is a
                # good choice for this.
                "provider_id": "urn:example:idp",

                # The organization slug is configured by setting the
                # `client_id` value. In this example, the SAML login URL is:
                #
                #     /accounts/saml/acme-inc/login/
                "client_id": "acme-inc",

                # The fields above are common `SocialApp` fields. For SAML,
                # additional configuration is needed, which is placed in
                # `SocialApp.settings`:
                "settings": {
                    # Mapping account attributes to upstream (IdP specific) attributes.
                    # If left empty, an attempt will be done to map the attributes using
                    # built-in defaults.
                    "attribute_mapping": {
                        "uid": "http://schemas.auth0.com/clientID",
                        "email_verified": "http://schemas.auth0.com/email_verified",
                        "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                    },
                    # The configuration of the IdP.
                    "idp": {
                        # The entity ID of the IdP is required.
                        "entity_id": "urn:example:idp",

                        # Then, you can either specify the IdP's metadata URL:
                        "metadata_url": "http://localhost:7000/metadata",

                        # Or, you can inline the IdP parameters here as follows:
                        "sso_url": "http://localhost:7000/saml/sso",
                        "slo_url": "http://localhost:7000/saml/sso",
                        "x509cert": """
-----BEGIN CERTIFICATE-----
MIIDuzCCAqOgAwIBAgIUDXNDFZ2oIwKSbaaZkc9j1bJZiWYwDQYJKoZIhvcNAQEL
BQAwbTELMAkGA1UEBhMCVVMxEzARBgNVBAgMCkNhbGlmb3JuaWExFjAUBgNVBAcM
DVNhbiBGcmFuY2lzY28xEDAOBgNVBAoMB0phbmt5Q28xHzAdBgNVBAMMFlRlc3Qg
SWRlbnRpdHkgUHJvdmlkZXIwHhcNMjQwNDE2MjA1NjM5WhcNNDQwNDExMjA1NjM5
WjBtMQswCQYDVQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwN
U2FuIEZyYW5jaXNjbzEQMA4GA1UECgwHSmFua3lDbzEfMB0GA1UEAwwWVGVzdCBJ
ZGVudGl0eSBQcm92aWRlcjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB
ANG0aOADtmQRKqs45IbY1jXSdKNkE9tEwxa4o4T1KLkzBngsQH/JA5P3Ejc7HE1G
ZtbXFcFmWck781yPsWJmlOw4FsPkrigbUOWgF5tf2/Ni/6xM6oeD/kO/+Xkk735y
m/oxEsdhRTECcdxxJvsce/Dbe/F5x+mSDv2ByT6yO1SZcDUSXroyHGZKpw0BXq8x
v+Vbxv6HJzTxVDJzq7aJSbzipIGCXdASbpAxCpvw+Hrzp47AXnuyAExxAtsLRvW6
fzXwBYngCHBGghu5QIX9/0/FO8BqCb/6LAZjvuDADnJEBWFPQ3PyOCCGOF0cn0cr
oTmhZfbMhL1HroXualTYJzcCAwEAAaNTMFEwHQYDVR0OBBYEFEBl/+Cl3QbtdCV2
zEnu7tEVmaAMMB8GA1UdIwQYMBaAFEBl/+Cl3QbtdCV2zEnu7tEVmaAMMA8GA1Ud
EwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAKVhn+P+0/IYHHLSa76V/O7T
ODoa85wYavusmo4/kcQESWKr5FEosLYATxBVbH/CEhSKB2xWbos6Mstw0gUmu54J
ji+Z6jaVyTgNgzSF7iEwN9tUAI9dOqvi9f1S3YbvowrXA/Kh0aKjXR3fmlfWB8z9
hwsZUiCGQ0L0HNoIc9asXWXt0N8a1UFyr4laEz6gGnajhG7Sf9I8vkbsvOYH8QOg
ok6KVoBFeXXkwxdQtFj7zftosd2jI9Qv+Ujt8D/iTseDDvzrVRFGKbNEpnS6ZDvD
y868b+Ihq4+MqPwBXKgIrjx7UL0ZUxEsXkgiMvesebpq0r1GcvBKv20/B5uS4KE=
-----END CERTIFICATE-----
""",
                    },
                },
            }]
        }
    }
            
WSGI_APPLICATION = 'ibvl.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.parse(DB)
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
    'http://localhost:3003',
    'http://localhost:3123',
    'http://'+DOMAIN,
    'https://'+DOMAIN
]

# Authentication
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS