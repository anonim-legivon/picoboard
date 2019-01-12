import logging

from .base import *
from .base import env

DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env('DJANGO_SECRET_KEY', default='!!!SET DJANGO_SECRET_KEY!!!')
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = 25432

MIDDLEWARE.insert(0, 'nplusone.ext.django.NPlusOneMiddleware')
NPLUSONE_LOGGER = logging.getLogger('nplusone')
NPLUSONE_LOG_LEVEL = logging.WARN
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'nplusone': {
            'level': 'WARN',
            'handlers': ['console'],
        }
    },
}

# Отключаем игнорирование ошибок кеширования редисом для дебага
CACHES['default']['OPTIONS']['IGNORE_EXCEPTIONS'] = False
