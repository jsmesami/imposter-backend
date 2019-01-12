import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False

SECRET_KEY = None  # must be set in instance-specific settings/local.py

ALLOWED_HOSTS = []

ADMINS = MANAGERS = (
    ('Ondřej Nejedlý', 'ondrej.nejedly@gmail.com'),
)

EMAIL_SUBJECT_PREFIX = '[Imposter] '

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'imposter',
        'CONN_MAX_AGE': 600,
        'USER': '',      # must be set in instance-specific settings/local.py
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

USE_I18N = True
USE_L10N = True
USE_TZ = False

TIME_ZONE = 'Europe/Prague'

LANGUAGE_CODE = 'cs'

MEDIA_ROOT = os.path.join(BASE_DIR, 'imposter/media')
MEDIA_URL = '/media/'

ROOT_URLCONF = 'imposter.urls'

WSGI_APPLICATION = 'imposter.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.postgres',
    'rest_framework',
    'imposter',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(process)d %(message)s',
        },
    },
    'filters': {
        'debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'syslog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'address': '/dev/log',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'imposter': {
            'level': 'DEBUG',
            'handlers': ['syslog', 'console'],
        },
    },
}

REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}

THUMBNAIL_PREFIX = 'CACHE/thumbnails/'

UPLOADED_FILE_MAX_SIZE = 3 * 1024 * 1024

SUPPORTED_IMAGE_EXTENSIONS = '.jpeg', '.jpg', '.png'

RENDERER = {
    'default_font_name': 'LiberationSans',
    'default_font_file': os.path.join(BASE_DIR, 'fonts', 'LiberationSans-Regular.ttf'),
    'default_font_size': 16,
    'default_text_color': '#000000',
    'jpg_print_params': {'dpi': '200', 'quality': 90},
    'jpg_thumb_params': {'dpi': '40', 'quality': 40}
}
