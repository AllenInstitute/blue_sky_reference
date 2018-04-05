import pytest
from pkg_resources import resource_filename
import os


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc'
    }


@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'queues': ('pbs', 'ingest')
    }

@pytest.fixture(scope='session')
def celery_enable_logging():
    return True


@pytest.fixture(scope='session')
def blue_sky_settings():
    os.environ['blue_sky_settings'] = \
        resource_filename(
            'blue_sky',
            os.path.join(
                '..',
                'config',
                'blue_sky_settings.yml'))

    import workflow_client.celery_ingest_consumer as celery_ingest_consumer

    return celery_ingest_consumer
