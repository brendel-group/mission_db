"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import environ
from corsheaders.defaults import default_headers

env = environ.Env(DEBUG=(bool, False), SECRET_KEY=(str, "unsafe-secret-key"))
# reading .env file
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-l$iff@-ubs*i$b$9e08v13q1v1^%pcv4w!-$7@-(@np1-&rrfv'
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".fly.dev"]
CSRF_TRUSTED_ORIGINS = [
    "https://*.fly.dev",
    "http://localhost:3000",
    "http://localhost:5173",
]

CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_HTTPONLY = False

SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SECURE = not DEBUG

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"

COOKIE_DOMAIN = env("COOKIE_DOMAIN", default=None)

SESSION_COOKIE_DOMAIN = COOKIE_DOMAIN

CSRF_COOKIE_DOMAIN = COOKIE_DOMAIN

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "rest_framework",
    "restapi",
    "corsheaders",
    "dj_rest_auth",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True


CORS_ALLOW_HEADERS = (
    *default_headers,
    "accept-ranges",
    "range",
)

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {"default": env.db()}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
    }

# Authentication
# https://dj-rest-auth.readthedocs.io/en/latest/configuration.html
REST_AUTH = {
    "TOKEN_MODEL": None,
}

USE_S3 = env("USE_S3", bool, False)

if USE_S3:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": env("AWS_STORAGE_BUCKET_NAME"),
                "custom_domain": f"{env('AWS_STORAGE_BUCKET_NAME')}.s3.eu-central-1.amazonaws.com",
                "object_parameters": {"CacheControl": "max-age=86400"},
                "cloudfront_key": open(env("AWS_CLOUDFRONT_KEY_FILE")).read(),
                "cloudfront_key_id": env("AWS_CLOUDFRONT_KEY_ID"),
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
    MEDIA_LOCATION = "media"
    MEDIA_URL = (
        f"https://{STORAGES['default']['OPTIONS']['custom_domain']}/{MEDIA_LOCATION}/"
    )

    STATIC_URL = "static/"

    STATIC_ROOT = BASE_DIR / "staticfiles"
else:
    MEDIA_ROOT = Path.joinpath(BASE_DIR, "media")
    MEDIA_URL = f"{env('DOMAIN', default='http://localhost:8000')}/file/download/"

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/5.1/howto/static-files/

    STATIC_URL = "static/"

    STATIC_ROOT = BASE_DIR / "staticfiles"

    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
