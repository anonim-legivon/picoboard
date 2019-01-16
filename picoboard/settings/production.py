from .base import env

SECRET_KEY = env('DJANGO_SECRET_KEY', default='!!!SET DJANGO_SECRET_KEY!!!')

ALLOWED_HOSTS = ['*']
