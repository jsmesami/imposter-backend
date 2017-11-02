# Save this file as local.py
from .base import *


DEBUG = True

ALLOWED_HOSTS = ('localhost',)

SECRET_KEY = "Make this unique and don't share with anybody."

# you may want to output emails to console:
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_PORT = 1025

# set correct credentials for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# on a Mac, syslog sits on a different path
# LOGGING['handlers']['syslog']['address'] = '/var/run/syslog'

# you may want to enable DRF browsable API
# REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
#     'rest_framework.renderers.JSONRenderer',
#     'rest_framework.renderers.BrowsableAPIRenderer',
# )
