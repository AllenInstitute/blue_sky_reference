import pytest
from mock import Mock, patch, mock_open
from workflow_engine.mixins import Runnable
from workflow_engine.models import (
    Job,
    Task,
    Workflow,
    WorkflowNode
)
from workflow_engine.workflow_config import WorkflowConfig
from django.contrib.contenttypes.models import ContentType
from blue_sky.models import Observation
from workflow_engine.strategies import ExecutionStrategy
from tests.workflow_configurations import (
    TEST_CONFIG_YAML_TWO_NODES,
)
from tests.workflow.workflow_fixtures import (
    run_states,      # noqa # pylint: disable=unused-import
)
from tests.signature_fixtures import (
    ENQUEUE_NEXT,
    SUBMIT_MOCK,
    KILL_MOAB_TASK,
    mock_celery_task  # noqa # pylint: disable=unused-import
)
from tests.strategy_fixtures import task_with_storage_directory # noqa # pylint: disable=unused-import


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


@patch('os.chmod')
def test_get_full_executable(
    mock_chmod,
    ex_strat,
    task_with_storage_directory):

    with patch('builtins.open', mock_open()):
        ex = ex_strat.get_full_executable(task_with_storage_directory)

    assert ex == (
        'mock.exe '
        '-mock_static mock_arguments '
        '--input_json '
        '/path/to/storage/mock_enqueued_object/10/jobs/job_789/tasks/task_123456/input_123456.json '
        '--output_json /path/to/storage/mock_enqueued_object/10/jobs/job_789/tasks/task_123456/output_123456.json'
    )
    mock_chmod.assert_called()


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
            'builtins.open',
            mock_open(read_data='{ "this": "that" }')):
            ex_strat.fail_execution_task(task)

    task.set_error_message.assert_called_once_with("Mock stdout")


def test_running_task(ex_strat):
    task = Mock()

    ex_strat.running_task(task)

@patch('os.path.isfile')
@patch('os.chmod')
def test_finish_task(
    mock_chmod,
    mock_isfile,
    ex_strat,
    task_with_storage_directory,
    mock_celery_task):

    with patch(ENQUEUE_NEXT, mock_celery_task):
        with patch(
            "builtins.open",
            mock_open(read_data='{ "data": "whatever" }')):
            ex_strat.finish_task(task_with_storage_directory)

    mock_chmod.assert_called()
    mock_isfile.assert_called_once_with(
        '/path/to/storage/mock_enqueued_object'
        '/10/jobs/job_789/tasks/task_123456/output_123456.json'
    )
    mock_celery_task.delay.assert_called_once_with(789)


@patch('os.path.isfile')
@patch('os.chmod')
def test_run_task(
    mock_chmod,
    mock_isfile,
    ex_strat,
    task_with_storage_directory):

    with patch('workflow_engine'
               '.celery'
               '.moab_tasks'
               '.submit_moab_task'
               '.apply_async') as mock_rat:
        with patch(
            "builtins.open",
            mock_open()):
            ex_strat.run_task(task_with_storage_directory)

    mock_rat.assert_called()


def test_kill_pbs_task(
    celery_worker,
    ex_strat,
    task_with_storage_directory,
    mock_celery_task):

    with patch(KILL_MOAB_TASK, mock_celery_task):
        ex_strat.kill_pbs_task(task_with_storage_directory)

    assert mock_celery_task.delay.called_once_with(5)


@pytest.mark.django_db
def test_run_asynchronous_task(
    ex_strat,
    mock_celery_task,
    run_states):
    WorkflowConfig.create_workflow_from_string(
        TEST_CONFIG_YAML_TWO_NODES
    )
    obs = Observation()
    obs.save()
    wf = Workflow.objects.get(
        name='test_workflow')
    wf.use_pbs = True
    wf.save()
    wns = WorkflowNode.objects.filter(
        workflow=wf)
    jb = Job(id=123,
             enqueued_object_id=obs.id,
             run_state_id=0,
             running_state=Runnable.STATE.PENDING,
             workflow_node=wns[0])
    jb.save()
    tsk = Task(job=jb,
               run_state_id=0,
               running_state=Runnable.STATE.PENDING,
               enqueued_task_object_type=ContentType.objects.get_for_model(
                   Observation
                ),
               enqueued_task_object_id=obs.id,
               enqueued_task_object=obs)
    tsk.save()

    with patch(SUBMIT_MOCK, mock_celery_task) as mock_submit:
        ex_strat.run_asynchronous_task(tsk)

    mock_submit.delay.assert_called_once()


@patch('os.chmod')
def test_get_output_file(
    mock_chmod,
    ex_strat,
    task_with_storage_directory):

    outfile = ex_strat.get_output_file(task_with_storage_directory)

    assert outfile == (
        '/path/to/storage/mock_enqueued_object'
        '/10/jobs/job_789/tasks/task_123456/output_123456.json'
    )


@patch('os.chmod')
def test_get_input_file(
    mock_chmod,
    ex_strat,
    task_with_storage_directory):

    infile = ex_strat.get_input_file(task_with_storage_directory)

    assert infile == (
        '/path/to/storage/mock_enqueued_object'
        '/10/jobs/job_789/tasks/task_123456/input_123456.json'
    )
    mock_chmod.assert_called()

@patch('os.chmod')
def test_get_pbs_file(
    mock_chmod,
    ex_strat,
    task_with_storage_directory):

    pbs_file = ex_strat.get_pbs_file(task_with_storage_directory)

    assert pbs_file == (
        '/path/to/storage/mock_enqueued_object'
        '/10/jobs/job_789/tasks/task_123456/pbs_123456.pbs'
    )
    mock_chmod.assert_called()


@patch('os.chmod')
def test_get_or_create_task_storage_directory(
    ex_strat,
    task_with_storage_directory):

    ex_strat.get_or_create_task_storage_directory(
        task_with_storage_directory
    )