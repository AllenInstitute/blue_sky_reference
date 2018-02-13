import pytest


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc'
    }


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


from workflow_client.celery_ingest_consumer import ingest_task
from workflow_client.client_settings import settings_attr_dict
