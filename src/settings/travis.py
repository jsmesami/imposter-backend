from .base import *  # NOQA


SECRET_KEY = "test"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'imposter',
        'USER': 'postgres',
        'PASSWORD': 'local',
        'HOST': '',
        'PORT': '',
    }
}
