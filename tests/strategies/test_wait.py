import pytest
from mock import Mock
from workflow_engine.strategies.wait_strategy \
    import WaitStrategy

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

    wait_strat.run_task(task)


def test_finish_task(wait_strat):
    task = Mock()

    wait_strat.finish_task(task)