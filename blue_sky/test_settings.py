"""
Django settings for blue_sky_test project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = BASE_DIR

#BASE_FILE_PATH = \
#    '/allen/programs/celltypes/workgroups/array_tomography/blue_sky/files/'
BASE_FILE_PATH = 'example_data'
PBS_FINISH_PATH = \
    '/allen/programs/celltypes/workgroups/array_tomography/blue_sky' + \
    '/at_em_imaging_workflow/pbs_execution_finish.py'

MESSAGE_QUEUE_NAME = 'at_em_imaging_workflow'
INGEST_QUEUE_NAME = 'em_2d_montage_ingest'
CELERY_MESSAGE_QUEUE_NAME = 'celery_' + MESSAGE_QUEUE_NAME
# CELERY_DEFAULT_QUEUE = 'celery_' + MESSAGE_QUEUE_NAME
CELERY_RESULT_BACKEND = 'django-db'

MESSAGE_QUEUE_HOST = 'message_queue'
MESSAGE_QUEUE_USER = 'blue_sky_user'
MESSAGE_QUEUE_PASSWORD = 'blue_sky_user'
MESSAGE_QUEUE_PORT = 5672

RENDER_SERVICE_URL = 'renderservice'
RENDER_SERVICE_PORT = '8080'
RENDER_SERVICE_USER = 'test_user'
RENDER_SERVICE_PROJECT = 'MM2'
RENDER_STACK_NAME = 'test_stack'
RENDER_CLIENT_SCRIPTS = '/path/to/render/scripts'
RENDER_POINT_MATCH_COLLECTION_NAME = 'default_point_matches'
MATLAB_SOLVER_PATH='/allen/aibs/pipeline/image_processing/volume_assembly/EMAligner/dev/allen_templates'
MONTAGE_SOLVER_BIN=os.path.join(MATLAB_SOLVER_PATH, 'solve_montage_SL')
RENDER_CLIENT_BASE_PATH='/allen/aibs/pipeline/image_processing/volume_assembly/render-jars/dev'
RENDER_CLIENT_SCRIPTS = os.path.join(RENDER_CLIENT_BASE_PATH, 'scripts')
RENDER_SPARK_JARFILE = os.path.join(RENDER_CLIENT_BASE_PATH, 'render-ws-spark-client-standalone.jar')
RENDER_CLIENT_JAR = os.path.join(RENDER_CLIENT_BASE_PATH, 'render-ws-java-client-standalone.jar')


FIJI_PATH = \
    '/allen/aibs/pipeline/image_processing/volume_assembly' + \
    '/Fiji.app/ImageJ-linux64'
SPARK_HOME='/allen/aibs/pipeline/image_processing/volume_assembly/utils/spark'
GRID_SIZE = 3
HEAP_SIZE = 10
INITIAL_SIGMA = 1.6
STEPS = 3
MIN_OCTAVE_SIZE = 800
MAX_OCTAVE_SIZE = 1200
FD_SIZE = 4
FD_BINS = 8

ROD = 0.92
MAX_EPSILON = 50
MIN_INLIER_RATIO = 0.0
MIN_NUMBER_INLIERS = 5
EXPECTED_MODEL_INDEX = 1
MULTIPLE_HYPOTHESES = True
REJECT_IDENTITY = True
IDENTITY_TOLERANCE = 5.0
TILES_ARE_IN_PLACE = True
DESIRED_MODEL_INDEX = 0
REGULARIZE = False
MAX_ITERATIONS_OPTIMIZE = 2000
MAX_PLATEAU_WIDTH_OPTIMIZE = 200
DIMENSION = 5
LAMBDA_VAL = 0.01
CLEAR_TRANSFORM = True
VISUALIZE = False

CHUNK_DEFAULTS = {
    'overlap': 2,
    'start_z': 1,
    'chunk_size': 10
}

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

APP_PACKAGE='blue_sky'
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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'database.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    },
    # Work around locked database table error w/ multiple processes
    'OPTIONS': {
        'timeout': 20
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'NumericPasswordValidator',
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
            'filename': os.environ.get('DEBUG_LOG', 'debug_test.log')
        },
    },
    'loggers': {
#        'django': {
#            'handlers': ['file'],
#            'level': 'WARN',
#            'propagate': True,
#        },
        'blue_sky': {
            'handlers': ['file'],
            'level': 'WARN',
            'propagate': True,
        },
        'test_output': {
            'handlers': ['file'],
            'level': 'DEBUG',
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

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

