"""
Django settings for blue_sky project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

APP_PACKAGE = 'blue_sky'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_FILE_PATH = '/allen/programs/celltypes/workgroups/em-connectomics/timf'

PBS_FINISH_PATH = '/data/aibstemp/timf/bswe'
MESSAGE_QUEUE_NAME = 'blue_sky'
INGEST_MESSAGE_QUEUE_NAME = 'ingest_' + MESSAGE_QUEUE_NAME
CELERY_MESSAGE_QUEUE_NAME = 'celery_' + MESSAGE_QUEUE_NAME
SPARK_MESSAGE_QUEUE_NAME = 'spark_' + MESSAGE_QUEUE_NAME
PBS_MESSAGE_QUEUE_NAME = 'pbs_' + MESSAGE_QUEUE_NAME

PBS_CONDA_HOME='/shared/utils.x86_64/python-2.7'
PBS_FINISH_MODULE='workflow_client.pbs_execution_finish'
PBS_PYTHONPATH='/data/aibstemp/timf/bswe'
PBS_CONDA_ENV='/allen/aibs/pipeline/image_processing/volume_assembly/conda_envs/blue_sky/py36'
PBS_RESPONSE_CONDA_ENV='/allen/aibs/pipeline/image_processing/volume_assembly/conda_envs/blue_sky/py36'

MESSAGE_QUEUE_HOST = 'ibs-timf-ux1.corp.alleninstitute.org'
MESSAGE_QUEUE_USER = 'blue_sky_user'
MESSAGE_QUEUE_PASSWORD = 'blue_sky_user'
MESSAGE_QUEUE_PORT = 9008
UI_HOST = 'ibs-timf-ux1.corp.alleninstitute.org'
UI_PORT = 9002
FLOWER_MONITOR_URL='http://' + UI_HOST + ":" + str(9003)
RABBIT_MONITOR_URL='http://' + UI_HOST + ":" + str(9000)
ADMIN_URL='http://' + UI_HOST + ':' + str(9002) + '/admin'

CONFIG_DIR = '/blue_sky/config'
BLUE_SKY_SETTINGS = '/blue_sky/config/blue_sky_settings.yml'
WORKFLOW_CONFIG_YAML = CONFIG_DIR + '/workflow_config.yml'

QMASTER_HOST = 'hpc-login.corp.alleninstitute.org'
QMASTER_PORT = 22
QMASTER_USERNAME = 'timf'
QMASTER_PASSWORD = CONFIG_DIR + '/blue_sky/config/crd'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qde=#m)tepmm$!n1j3+b8#!mz_s-pn2@2soe@9^_ol8363pjlp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

RESULTS_PER_PAGE = 20

MAX_DISPLAYED_PAGE_LINKS = 10

WORKFLOW_VERSION = 0.1

MILLISECONDS_BETWEEN_REFRESH = 10000
# MILLISECONDS_BETWEEN_REFRESH = 1000

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'workflow_engine',
    'workflow_client',
    'django_celery_results',
    'blue_sky'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = APP_PACKAGE + '.urls'

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

WSGI_APPLICATION = 'blue_sky.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blue_sky',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'ibs-timf-ux1',
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Pacific'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        }
    },    
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.environ.get('DEBUG_LOG',
                                       'logs/debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARN',
            'propagate': True,
        },
        'blue_sky': {
            'handlers': ['file'],
            'level': 'WARN',
            'propagate': True,
        },
        'workflow_engine': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery.task': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }        
    }
}

CELERYD_HIJACK_ROOT_LOGGER = False
