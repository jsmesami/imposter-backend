from django.core.exceptions import ImproperlyConfigured


try:
    from .local import *
except ImportError:
    raise ImproperlyConfigured('Please provide instance-specific settings/local.py (see settings/local_example.py).')

if SECRET_KEY == "Make this unique and don't share with anybody.":
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured('Please set SECRET_KEY in settings/local.py to a unique, unpredictable value.')
