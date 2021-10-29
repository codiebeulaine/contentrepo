import os
import environ

env = environ.Env()

DEBUG = True
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)
# SECURITY WARNING: keep the secret key used in production secret!
DEFAULT_SECRET_KEY = "please-change-me"
SECRET_KEY = os.environ.get("SECRET_KEY") or DEFAULT_SECRET_KEY
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    [
        "*",
    ],
)
INSTALLED_APPS = [
    "home",
    "search",
    "menu",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail_content_import",
    "wagtail_content_import.pickers.google",
    "wagtail_content_import.pickers.local",
    "wagtail.admin",
    "wagtail.core",
    "wagtail.locales",
    "wagtail.api.v2",
    "wagtailmedia",
    "wagtail.contrib.simple_translation",
    "rest_framework",
    "rest_framework.authtoken",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "contentrepo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
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

WSGI_APPLICATION = "contentrepo.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]


STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"  # noqa
)

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


# Wagtail settings

WAGTAIL_SITE_NAME = "contentrepo"
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("ar", "Arabic"),
    ("id", "Bahasa"),
    ("bn", "Bangla"),
    ("zh", "Chinese"),
    ("prs", "Dari"),
    ("en", "English"),
    ("fr", "French"),
    ("ha", "Hausa"),
    ("hi", "Hindi"),
    ("it", "Italian"),
    ("ku", "Kurdish"),
    ("lv", "Latvian"),
    ("ps", "Pashto"),
    ("pl", "Polish"),
    ("pt", "Portuguese"),
    ("ru", "Russian"),
    ("so", "Somali"),
    ("es", "Spanish"),
    ("sw", "Swahili"),
    ("ur", "Urdu"),
]

# Base URL to use when referring to full URLs
# within the Wagtail admin backend
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = os.environ.get("BASE_URL", "http://example.com")

WAGTAILCONTENTIMPORT_DEFAULT_MAPPER = "home.mappers.ContentMapper"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_LOCATION", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",  # noqa
    "PAGE_SIZE": env.int("PAGE_SIZE", 5),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ContentRepo API",
    "VERSION": "1.0.0",
}
