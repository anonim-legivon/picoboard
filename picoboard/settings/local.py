import logging

from .base import *
from .base import env

DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env('DJANGO_SECRET_KEY', default='!!!SET DJANGO_SECRET_KEY!!!')
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = 15432

MIDDLEWARE.insert(0, 'nplusone.ext.django.NPlusOneMiddleware')
NPLUSONE_LOGGER = logging.getLogger('nplusone')
NPLUSONE_LOG_LEVEL = logging.WARN

LOGGING['loggers']['nplusone'] = {
    'handlers': ['console'],
    'level': 'WARN',
}

# Отключаем игнорирование ошибок кеширования редисом для дебага
CACHES['default']['OPTIONS']['IGNORE_EXCEPTIONS'] = False

# Celery
# ------------------------------------------------------------------------------
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = True
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True
