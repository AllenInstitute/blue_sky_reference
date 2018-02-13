import pytest
from mock import Mock, patch, mock_open
from mock.mock import _patch_object
from workflow_engine.strategies.execution_strategy \
    import ExecutionStrategy

try:
    import __builtin__ as builtins  # @UnresolvedImport
except:
    import builtins  # @UnresolvedImport


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


@patch('os.path.isfile', Mock(return_value=True))
def test_set_error_message_from_log(ex_strat):
    task = Mock()
    task.set_error_message = Mock()

    result = Mock()
    result.stdout.decode = Mock(return_value="Mock stdout")

    with patch('subprocess.run', Mock(return_value=result)):
        ex_strat.set_error_message_from_log(task)

    task.set_error_message.assert_called_once_with("Mock stdout")


@patch('os.path.isfile', Mock(return_value=True))
def test_fail_execution_task(ex_strat):
    task = Mock()
    task.set_error_message = Mock()

    result = Mock()
    result.stdout.decode = Mock(return_value="Mock stdout")

    with patch('subprocess.run', Mock(return_value=result)):
        with patch(
            builtins.__name__ + '.open',
            mock_open(read_data='{ "this": "that" }')):
            ex_strat.fail_execution_task(task)

    task.set_error_message.assert_called_once_with("Mock stdout")


def test_running_task(ex_strat):
    task = Mock()

    ex_strat.running_task(task)


def test_finish_task(ex_strat):
    task = Mock()
    task.id = 123
    enqueued_obj = Mock()
    enqueued_obj.id = 555
    task.job = Mock()
    task.job.id = 777
    task.job.get_enqueued_object = Mock(return_value = enqueued_obj)
    task.job.workflow_node.get_children = Mock(return_value=[])

    with patch(
        'workflow_engine.workflow_controller.WorkflowController.get_enqueued_object',
        return_value=enqueued_obj):
        with patch(
            'os.path.isfile',
            Mock(return_value=True)) as mock_isfile:
            with patch(
                builtins.__name__ + ".open",
                mock_open(read_data='{ "data": "whatever" }')):
                ex_strat.finish_task(task)

    mock_isfile.assert_called_once_with(
        'example_data/555/jobs/job_777/tasks/task_123/output_123.json')
    task.job.get_enqueued_object.assert_called_once()
    task.job.workflow_node.get_children.assert_called_once()

def test_run_task(ex_strat):
    task = Mock()

    ex_strat.run_task(task)


@pytest.mark.skipif(True, reason='need better mock')
def test_kill_pbs_task(
    celery_session_worker,
    ex_strat):
    task = Mock()
    task.pbs_id = 5

    with patch('workflow_client.worker_client.run_server_command'):
        result = ex_strat.kill_pbs_task(task)
        result.get()


@pytest.mark.skipif(True, reason='need better mock')
def test_run_asynchronous_task(ex_strat):
    task = Mock()

    ex_strat.run_asynchronous_task(task)


def test_get_output_file(ex_strat):
    task = Mock()

    ex_strat.get_output_file(task)


def test_get_input_file(ex_strat):
    task = Mock()

    ex_strat.get_input_file(task)


def test_get_pbs_file(ex_strat):
    task = Mock()

    ex_strat.get_pbs_file(task)


def test_get_or_create_task_storage_directory(ex_strat):
    task = Mock()

    ex_strat.get_or_create_task_storage_directory(task)