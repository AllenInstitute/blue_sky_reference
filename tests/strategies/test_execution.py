import pytest
from mock import Mock, patch, mock_open
from workflow_engine.models.task import Task
from blue_sky.models.observation import Observation
from workflow_engine.models.job import Job
from workflow_engine.models.run_state import RunState
import os
from workflow_engine.workflow_config import WorkflowConfig
from workflow_engine.models.workflow import Workflow
from workflow_engine.models.workflow_node import WorkflowNode
from workflow_engine.strategies.execution_strategy \
    import ExecutionStrategy
from tests.workflow_configurations \
    import TEST_CONFIG_YAML_TWO_NODES


@pytest.fixture
def ex_strat():
    return ExecutionStrategy()


def xest_get_input_data(ex_strat):
    enqueued_object = Mock()
    task = Mock()
    storage_directory = '/example/storage/directory'

    inp = ex_strat.get_input(
        enqueued_object,
        storage_directory,
        task)
    assert inp is not None


def xest_get_executable(ex_strat):
    task = Mock()

    ex = ex_strat.get_executable(task)
    
    assert ex is not None


@pytest.mark.skipif(True, reason='mock dir creation')
def xest_get_full_executable(ex_strat):
    task = Mock()

    ex = ex_strat.get_full_executable(task)

    assert ex is not None


def xest_skip_execution(ex_strat):
    enqueued_object = Mock()

    skip = ex_strat.skip_execution(enqueued_object)

    assert skip == False


@patch('os.path.isfile', Mock(return_value=True))
def xest_set_error_message_from_log(ex_strat):
    task = Mock()
    task.set_error_message = Mock()

    result = Mock()
    result.stdout.decode = Mock(return_value="Mock stdout")

    with patch('subprocess.run', Mock(return_value=result)):
        ex_strat.set_error_message_from_log(task)

    task.set_error_message.assert_called_once_with("Mock stdout")


@patch('os.path.isfile', Mock(return_value=True))
def xest_fail_execution_task(ex_strat):
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


def xest_running_task(ex_strat):
    task = Mock()

    ex_strat.running_task(task)


def xest_finish_task(ex_strat):
    task = Mock()
    task.id = 123
    enqueued_obj = Mock()
    enqueued_obj.id = 555
    task.job = Mock()
    task.job.id = 777
    task.job.get_enqueued_object = Mock(return_value = enqueued_obj)

    mock_enqueue_next = Mock(
        name='mock_enqueue_next')
    mock_enqueue_next.delay = Mock()

    with patch(
        'workflow_engine.strategies.execution_strategy.enqueue_next_queue_signature',
        mock_enqueue_next):
        with patch(
            'workflow_engine.workflow_controller.WorkflowController.get_enqueued_object',
            return_value=enqueued_obj):
            with patch(
                'os.path.isfile',
                Mock(return_value=True)) as mock_isfile:
                with patch(
                    "builtins.open",
                    mock_open(read_data='{ "data": "whatever" }')):
                    ex_strat.finish_task(task)

    mock_isfile.assert_called_once_with(
        'example_data/555/jobs/job_777/tasks/task_123/output_123.json')
    mock_enqueue_next.delay.assert_called_once_with(777)
    #task.job.get_enqueued_object.assert_called_once()
    #task.job.workflow_node.get_children.assert_called_once()

def xest_run_task(ex_strat):
    task = Mock()

    ex_strat.run_task(task)


@pytest.mark.skipif(True, reason='need better mock')
def xest_kill_pbs_task(
    celery_worker,
    ex_strat):
    task = Mock()
    task.pbs_id = 5

    with patch('workflow_client.worker_client.run_server_command'):
        result = ex_strat.kill_pbs_task(task)
        result.get()


@pytest.mark.django_db
def test_run_asynchronous_task(ex_strat):
    with patch("builtins.open",
        mock_open(read_data=TEST_CONFIG_YAML_TWO_NODES)):
        WorkflowConfig.create_workflow(
            os.path.join(os.path.dirname(__file__),
                         'dev.yml'))
        obs = Observation()
        obs.save()
        pend = RunState.objects.get(name="PENDING")
        pend.save()
        wf = Workflow.objects.get(
            name='test_workflow')
        wf.use_pbs = True
        wf.save()
        wns = WorkflowNode.objects.filter(
            workflow=wf)
        jb = Job(id=123,
                 enqueued_object_id=obs.id,
                 run_state=pend,
                 workflow_node=wns[0])
        jb.save()
        tsk = Task(job=jb,
                   run_state=pend,
                   enqueued_task_object_class='blue_sky.models.observation.Observation',
                   enqueued_task_object_id=obs.id)
        tsk.save()
        with patch('workflow_engine'
                   '.celery'
                   '.moab_tasks'
                   '.submit_moab_task'
                   '.apply_async') as mock_rat:
            ex_strat.run_asynchronous_task(tsk)

        mock_rat.assert_called()


def xest_get_output_file(ex_strat):
    task = Mock()

    ex_strat.get_output_file(task)


def xest_get_input_file(ex_strat):
    task = Mock()

    ex_strat.get_input_file(task)


def xest_get_pbs_file(ex_strat):
    task = Mock()

    ex_strat.get_pbs_file(task)


def xest_get_or_create_task_storage_directory(ex_strat):
    task = Mock()

    ex_strat.get_or_create_task_storage_directory(task)