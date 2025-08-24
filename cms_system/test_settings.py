"""
Test settings for the CMS system
"""
from .settings import *
import os
import sys

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use console email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable Celery for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use simple cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Mock external services for tests
OPENSEARCH_HOST = 'mock:9200'
KAFKA_BOOTSTRAP = 'mock:9092'

# Test secret key
SECRET_KEY = 'test-secret-key-for-testing-only'

# Disable debug for tests
DEBUG = False

# Disable CSRF for tests
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False

# Test media and static settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
STATIC_ROOT = os.path.join(BASE_DIR, 'test_static')

# Disable logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable signals during tests to prevent default data creation
SIGNALS_DISABLED = True

# Test-specific REST framework settings
REST_FRAMEWORK.update({
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
})

# Ensure test apps are in INSTALLED_APPS
if 'users' not in INSTALLED_APPS:
    INSTALLED_APPS.append('users')
if 'cms' not in INSTALLED_APPS:
    INSTALLED_APPS.append('cms')
if 'discovery' not in INSTALLED_APPS:
    INSTALLED_APPS.append('discovery')
if 'external_sources' not in INSTALLED_APPS:
    INSTALLED_APPS.append('external_sources')
