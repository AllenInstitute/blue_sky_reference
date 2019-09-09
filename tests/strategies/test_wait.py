import pytest
from mock import Mock, patch
from workflow_engine.strategies.wait_strategy import WaitStrategy
from tests.strategy_fixtures import task_with_storage_directory # noqa # pylint: disable=unused-import
from tests.signature_fixtures import (
    ENQUEUE_NEXT,
    mock_celery_task  # noqa # pylint: disable=unused-import
)


@pytest.fixture
def wait_strat():
    return WaitStrategy()


def test_must_wait(wait_strat):
    enqueued_object = Mock()

    w = wait_strat.must_wait(enqueued_object)
    assert w == True


def test_skip_execution(wait_strat):
    enqueued_object = Mock()

    w = wait_strat.skip_execution(enqueued_object)
    assert w == True


def test_run_task(wait_strat):
    task = Mock()
    task.enqueued_task_object = Mock()

    wait_strat.run_task(task)


@pytest.mark.django_db(transaction=True)
def test_finish_task(
    wait_strat,
    task_with_storage_directory,
    mock_celery_task):

    with patch(ENQUEUE_NEXT, mock_celery_task):
        wait_strat.finish_task(task_with_storage_directory)