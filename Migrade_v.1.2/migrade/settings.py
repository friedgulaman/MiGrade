"""
Django settings for geeksforgeeks project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
from django.conf.urls.static import static
import sys
import os
from dotenv import load_dotenv
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.getenv("EMAIL_PORT")

EMAIL_USE_TLS = EMAIL_USE_TLS
EMAIL_HOST = EMAIL_HOST
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_PORT = EMAIL_PORT

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_DEBUG = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
django = os.getenv("DJANGO")
public = os.getenv("RECAPTCHA_PUBLIC_KEY")
private = os.getenv("RECAPTCHA_PRIVATE_KEY ")
SECRET_KEY = django


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['192.168.1.4']
# http://127.0.0.1:8000/

# ALLOWED_HOSTS = ['192.168.43.70','192.168.18.21', 'localhost', '127.0.0.1', '131.226.107.101', '192.168.43.70', '192.168.18.1', '192.168.1.134']




# Application definition

INSTALLED_APPS = [
    'view_breadcrumbs',
    'captcha',
    'CuyabSRMS',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'migrade.urls'

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
                'django.template.context_processors.media',
                'CuyabSRMS.AdminViews.admin_base',
                'CuyabSRMS.TransferRecordViews.inbox_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'migrade.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'migrade_v.2.1',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',   
        'PORT': '3306',
    }    
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Optional
    ],
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"  # or "django.contrib.sessions.backends.cache", etc.
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # Set session expiration time to 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'sessionid_user'
CSRF_COOKIE_NAME = 'csrftoken'
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True


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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_L10N = True

USE_TZ = True



STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Include your project's static files
    os.path.join(BASE_DIR, 'static/node_modules/bootstrap/dist'), 
    os.path.join(BASE_DIR, 'static/star-admin/'),  
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Set a STATIC_ROOT if you plan to collect static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000  # Adjust the number as needed


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# AUTHENTICATION_BACKENDS= ['CuyabSRMS.EmailBackEnd.EmailBackEnd']

AUTH_USER_MODEL = 'CuyabSRMS.CustomUser'


AUTHENTICATION_BACKENDS = [
    'CuyabSRMS.EmailBackEnd.EmailBackEnd',
    'django.contrib.auth.backends.ModelBackend',  # You can keep the default backend too.
]

RECAPTCHA_PUBLIC_KEY = public
RECAPTCHA_PRIVATE_KEY = private



# Define the base directory where uploaded files will be stored
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # or any large number that suits your needs
PASSWORD_RESET_TIMEOUT_MINUTES = 15
