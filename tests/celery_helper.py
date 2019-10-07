import pytest


@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'queues': ('pbs', 'ingest')
    }

@pytest.fixture(scope='session')
def celery_enable_logging():
    return True
