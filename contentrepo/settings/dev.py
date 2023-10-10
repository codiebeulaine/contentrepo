from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

WHATSAPP_API_URL = "http://whatsapp"
WHATSAPP_ACCESS_TOKEN = "fake-access-token"  # noqa: S105 (This is a test config.)
FB_BUSINESS_ID = "27121231234"


# NOTE: We don't want the cache getting in the way during tests, but this also
# means we're not testing the cache behaviour.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
