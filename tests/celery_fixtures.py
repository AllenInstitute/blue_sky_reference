from celery.contrib.pytest import celery_app  # noqa # pylint: disable=unused-import
from workflow_client.simple_router import SimpleRouter
from workflow_client.client_settings import configure_worker_app
from mock import Mock, patch
import pytest


@pytest.fixture(autouse=True)
def celery_enable_logging():
    return True


@pytest.fixture(autouse=True)
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc'
    }


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
@patch('workflow_client.client_settings.get_message_broker_url',
        Mock(return_value='memory://'))
def result_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'result')

    return celery_app

@pytest.fixture
@patch('workflow_client.client_settings.get_message_broker_url',
        Mock(return_value='memory://'))
def ingest_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'ingest')

    return celery_app

@pytest.fixture
@patch('workflow_client.client_settings.get_message_broker_url',
        Mock(return_value='memory://'))
def workflow_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'workflow')

    return celery_app
