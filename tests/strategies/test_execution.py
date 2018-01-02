import pytest
from mock import Mock
from workflow_engine.strategies.execution_strategy \
    import ExecutionStrategy

@pytest.fixture
def ex_strat():
    return ExecutionStrategy()


def test_get_input_data(ex_strat):
    enqueued_object = Mock()
    task = Mock()
    storage_directory = '/example/storage/directory'

    inp = ex_strat.get_input(
        enqueued_object,
        storage_directory,
        task)
    assert inp is not None


def test_get_executable(ex_strat):
    task = Mock()

    ex = ex_strat.get_executable(task)
    
    assert ex is not None


@pytest.mark.skipif(True, reason='mock dir creation')
def test_get_full_executable(ex_strat):
    task = Mock()

    ex = ex_strat.get_full_executable(task)
    
    assert ex is not None


def test_skip_execution(ex_strat):
    enqueued_object = Mock()

    skip = ex_strat.skip_execution(enqueued_object)
    
    assert skip == False


def test_set_error_message_from_log(ex_strat):
    task = Mock()

    ex_strat.set_error_message_from_log(task)


def test_fail_execution_task(ex_strat):
    task = Mock()

    ex_strat.fail_execution_task(task)


def test_running_task(ex_strat):
    task = Mock()

    ex_strat.running_task(task)


def test_finish_task(ex_strat):
    task = Mock()

    ex_strat.finish_task(task)


def test_run_task(ex_strat):
    task = Mock()

    ex_strat.run_task(task)


@pytest.mark.skipif(True, reason='need better mock')
def test_kill_pbs_task(ex_strat):
    task = Mock()

    ex_strat.kill_pbs_task(task)


@pytest.mark.skipif(True, reason='need better mock')
def test_run_asynchronous_task(ex_strat):
    task = Mock()

    ex_strat.run_asynchronous_task(task)


@pytest.mark.skipif(True, reason='need better mock')
def test_get_output_file(ex_strat):
    task = Mock()

    ex_strat.get_output_file(task)


@pytest.mark.skipif(True, reason='need better mock')
def test_get_input_file(ex_strat):
    task = Mock()

    ex_strat.get_input_file(task)


@pytest.mark.skipif(True, reason='need better mock')
def test_get_pbs_file(ex_strat):
    task = Mock()

    ex_strat.get_pbs_file(task)


@pytest.mark.skipif(True, reason='need better mock')
def test_get_or_create_task_storage_directory(ex_strat):
    task = Mock()

    ex_strat.get_or_create_task_storage_directory(task)