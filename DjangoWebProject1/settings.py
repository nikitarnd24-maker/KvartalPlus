from pathlib import Path
import os
from dotenv import load_dotenv

# переменные окружения из .env файла
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# БАЗОВЫЕ НАСТРОЙКИ

SECRET_KEY = os.getenv('SECRET_KEY', '5eef9da7-9318-4181-9693-e16e58f68539')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '::1',
    '213.171.7.125',
    'kvartalplus.ru',
    'www.kvartalplus.ru',
]
extra_hosts = os.getenv('ALLOWED_HOSTS_EXTRA', '').split(',')
ALLOWED_HOSTS.extend([host for host in extra_hosts if host])


# ПРИЛОЖЕНИЯ

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# URLS / WSGI
ROOT_URLCONF = 'DjangoWebProject1.urls'
WSGI_APPLICATION = 'DjangoWebProject1.wsgi.application'

# ШАБЛОНЫ
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# БАЗА ДАННЫХ (SQLite)
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
    }
}

# ПАРОЛИ
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:63442',
    'http://127.0.0.1:63442',
    'http://213.171.7.125',
    'https://kvartalplus.ru',
    'https://www.kvartalplus.ru',
] 
extra_origins = os.getenv('CSRF_TRUSTED_ORIGINS_EXTRA', '').split(',')
CSRF_TRUSTED_ORIGINS.extend([origin for origin in extra_origins if origin])

# ЛОКАЛИЗАЦИЯ
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# СТАТИКА
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'app' / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ПРОЧЕЕ
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# TELEGRAM
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8287575486:AAEwPqyBfSodh22sOqHjh6qqBPfBdOT0ScU')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1003291809033')

# БЕЗОПАСНОСТЬ
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ЛОГИРОВАНИЕ
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django_errors.log',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}