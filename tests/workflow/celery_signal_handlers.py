from django.conf import settings
import celery
import os
import logging


@celery.signals.after_setup_task_logger.connect
def after_setup_celery_task_logger(logger, **kwargs):
    os.environ['DEBUG_LOG'] = 'test_debug.log'
    logging.config.dictConfig(settings.LOGGING)
