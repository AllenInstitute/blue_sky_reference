import pytest
from mock import Mock


ENQUEUE_NEXT = (
    'workflow_engine.strategies.execution_strategy.'
    'enqueue_next_queue_signature'
)
KILL_MOAB_TASK = (
    'workflow_engine.strategies.execution_strategy.'
    'kill_moab_task_signature'
)
SUBMIT_MOCK = (
    'workflow_engine.strategies.execution_strategy.'
    'submit_mock_signature'
)

@pytest.fixture
def mock_celery_task():
    mock_task = Mock()
    mock_task.delay = Mock()
    mock_task.apply_async = Mock()

    return mock_task
