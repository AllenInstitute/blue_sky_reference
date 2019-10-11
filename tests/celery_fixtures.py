from celery.contrib.pytest import celery_app  # noqa # pylint: disable=unused-import
from workflow_engine.simple_router import SimpleRouter
from workflow_engine.client_settings import configure_worker_app
import pytest


@pytest.fixture(autouse=True)
def celery_enable_logging():
    return True


@pytest.fixture(autouse=True)
def use_celery_app_trap():
    return True

def celery_worker_parameters_helper(worker_name):
    router = SimpleRouter('blue_sky')

    queues = ['{}@blue_sky'.format(worker_name)]

    if worker_name != 'result':
        queues.append('result@blue_sky')

    return {
        'queues': queues,
        'router': (router.route_task,),
        'perform_ping_check': False
    }


def celery_includes_helper(module_strings):
    module_strings.append('tests.workflow.celery_signal_handlers')
    return module_strings

@pytest.fixture
def result_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'result')

    return celery_app

@pytest.fixture
def ingest_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'ingest')

    return celery_app

@pytest.fixture
def workflow_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'workflow')

    return celery_app
