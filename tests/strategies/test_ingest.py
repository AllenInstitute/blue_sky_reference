import pytest
from mock import Mock, patch, MagicMock
from tests.signature_fixtures import (
    ENQUEUE_NEXT,
    mock_celery_task  # noqa # pylint: disable=unused-import
)
from workflow_engine.strategies.ingest_strategy import IngestStrategy


@pytest.fixture
def task_to_enqueue():
    task = Mock()
    task.job = Mock()
    task.job.id = 5
    task.job.all_tasks_finished = Mock(return_value=True)

    return task


@pytest.fixture
def in_strat():
    return IngestStrategy()


def test_get_workflow_name(in_strat):
    default_name = in_strat.get_workflow_name()

    assert default_name is None


def test_skip_execution(in_strat):
    enqueued_object = Mock()

    skip = in_strat.skip_execution(enqueued_object)
    
    assert skip is True


def test_create_enqueued_object(in_strat):
    dictionary = Mock()

    default_obj, default_start_node = in_strat.create_enqueued_object(
        dictionary
    )

    assert default_obj is None
    assert default_start_node is None


def test_generate_response(in_strat):
    enqueued_object = Mock()

    default_response = in_strat.generate_response(enqueued_object)
    
    assert default_response is None


def test_is_ingest_strategy(in_strat):
    is_ingest = in_strat.is_ingest_strategy()
    
    assert is_ingest is True


def test_run_task(
    in_strat,
    task_to_enqueue,
    mock_celery_task):
    '''Run an ingest strategy, verify the task enqueued message is sent.
    '''
    with patch(ENQUEUE_NEXT, mock_celery_task):
        result = in_strat.run_task(task_to_enqueue)

    assert result == None
    task_to_enqueue.job.all_tasks_finished.assert_called_once()
    mock_celery_task.delay.assert_called_once_with(5)


def test_finish_task(
    in_strat,
    task_to_enqueue,
    mock_celery_task):

    with patch(ENQUEUE_NEXT, mock_celery_task):
        in_strat.finish_task(task_to_enqueue)

    task_to_enqueue.job.all_tasks_finished.assert_called_once()
    mock_celery_task.delay.assert_called_once_with(5)


def test_call_ingest_strategy():
    wf_name = 'test_workflow_name'
    msg = 'test_message'
    
    with patch('workflow_engine.models.workflow.Workflow.objects.get'):
        with patch('workflow_engine.strategies.ingest_strategy.import_class',
                   MagicMock()):
            IngestStrategy.call_ingest_strategy(wf_name, msg)
