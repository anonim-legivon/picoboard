"""
Django settings for picoboard project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys

import environ
from corsheaders.defaults import default_headers

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', False)

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_regex',
    'netfields',
    'recaptcha',
]
LOCAL_APPS = [
    'core',
    'board',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'picoboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'picoboard.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': env.str('POSTGRES_USER', 'picoboard'),
        'PASSWORD': env.str('POSTGRES_PASSWORD', 'picoboard'),
        'HOST': env.str('POSTGRES_HOST', 'postgres'),
        'PORT': env.int('POSTGRES_PORT', 5432),
        'NAME': env.str('POSTGRES_DB', 'picoboard'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': env.int('CONN_MAX_AGE', default=60)
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Vladivostok'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ADMIN_SITE_HEADER = 'PICOBOARD'

APPEND_SLASH = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

VAR_PATH = os.path.join(BASE_DIR, 'etc')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(VAR_PATH, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(VAR_PATH, 'static')

for path in (VAR_PATH, MEDIA_ROOT):
    if not os.path.exists(path):
        os.mkdir(path)

# django-redis cache
CACHE_REDIS_HOSTS = env.str('REDIS_URL', 'redis://redis:6379/0')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CACHE_REDIS_HOSTS,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', 'redis://redis:6379/2')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ACKS_LATE = True
# CELERY_BEAT_SCHEDULE = {
#     'clear-db': {
#         'task': 'board.tasks.clear_db',
#         'schedule': crontab(minute='*/1')
#     },
#     'bump-limit-threads': {
#         'task': 'board.tasks.bump_limit_threads',
#         'schedule': crontab(minute='*/1')
#     }
# }

CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', True)
CORS_ORIGIN_WHITELIST = env.list('CORS_ORIGIN_WHITELIST', str, '*')
CORS_ALLOW_HEADERS = default_headers + ('Company', 'Cache-Control')

# Cooldown settings
COOLDOWN_SECONDS_THREAD = env.int('COOLDOWN_SECONDS_THREAD', 360)
COOLDOWN_SECONDS_POST = env.int('COOLDOWN_SECONDS_POST', 5)

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'SEARCH_PARAM': 'q',
    'DEFAULT_THROTTLE_CLASSES': (
        'core.throttling.CustomScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'thread.create': COOLDOWN_SECONDS_THREAD,
        'thread.new_post': COOLDOWN_SECONDS_POST,
    },
    'EXCEPTION_HANDLER': 'core.exceptions.api_exception_handler',
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60,
    'DATETIME_FORMAT': '%s',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'WARNING',
        'handlers': [],
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

GR_CAPTCHA_SECRET_KEY = env.str('RECAPTCHA_SECRET_KEY', None)
