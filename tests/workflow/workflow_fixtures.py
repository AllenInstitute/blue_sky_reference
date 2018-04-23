import pytest
from django.utils import timezone
from blue_sky.models.observation import Observation
from _pytest.hookspec import pytest_fixture_post_finalizer


@pytest.fixture
def run_states():
    rs = {}
    for s in [
        'PENDING',
        'QUEUED',
        'RUNNING',
        'FINISHED_EXECUTION',
        'FAILED_EXECUTION',
        'SUCCESS',
        'FAILED']:
        rs[s], _ = RunState.objects.update_or_create(
            name=s)
    return rs


@pytest.fixture
def obs():
    (o, _) = Observation.objects.update_or_create(
        arg1='5',
        arg2='Whatever',
        arg3='Something',
        proc_state='CONTEMPLATIVE')

    return o


@pytest.fixture
def waiting_task(run_states):
    workflow, _ = Workflow.objects.update_or_create(
        id=1,
        name="analyze",
        ingest_strategy_class='blue_sky.strategies.mock_ingest.MockIngest')
    job_queue, _ = JobQueue.objects.update_or_create(
        id=8,
        name='Mock Wait',
        enqueued_object_class='blue_sky.models.observation.Observation',
        job_strategy_class='blue_sky.strategies.mock_wait.MockWait',
        defaults={})
    workflow_node, _ = WorkflowNode.objects.update_or_create(
        id=1,
        defaults={
            'workflow': workflow,
            'job_queue': job_queue})
    waiter_obs,_ = Observation.objects.update_or_create(
        id=72,
        arg1='5',
        arg2='Whatever',
        arg3='Something',
        proc_state='CONTEMPLATIVE')
    job, _ = Job.objects.update_or_create(
        id=9,
        defaults = {
            'enqueued_object_id': waiter_obs.id,
            'run_state': run_states['PENDING'],
            'workflow_node': workflow_node})
#     task, _ = Task.objects.update_or_create(
#         id=8,
#         job=job,
#         defaults={
#             'full_executable': 'mock_task',
#             'run_state': run_states['PENDING'],
#             'start_run_time': timezone.now()})

    return job


@pytest.fixture
def task_5(run_states):
    workflow, _ = Workflow.objects.update_or_create(
        id=1,
        name="analyze",
        ingest_strategy_class='blue_sky.strategies.mock_ingest.MockIngest')
    job_queue, _ = JobQueue.objects.update_or_create(
        id=7,
        name='Mock Analyze',
        enqueued_object_class='blue_sky.models.observation.Observation',
        job_strategy_class='blue_sky.strategies.mock_ingest.MockIngest',
        defaults={})
    workflow_node, _ = WorkflowNode.objects.update_or_create(
        id=1,
        defaults={
            'workflow': workflow,
            'job_queue': job_queue})
    job, _ = Job.objects.update_or_create(
        id=2,
        defaults = {
            'enqueued_object_id': 56,
            'run_state': run_states['PENDING'],
            'workflow_node': workflow_node})
    task, _ = Task.objects.update_or_create(
        id=5,
        job=job,
        defaults={
            'full_executable': 'mock_task',
            'run_state': run_states['PENDING'],
            'start_run_time': timezone.now()})

    return task

@pytest.fixture
def mock_executable():
    (ex, _) = Executable.objects.update_or_create(
        name='Mock Executable',
        executable_path='/path/to/mock/executable.sh',
        static_arguments='-this is -a test',
        remote_queue='pbs',
        pbs_queue='mock-pbs-queue',
        pbs_processor='nodes-1:ppn=1',
        pbs_walltime='walltime=0:10:00')

    return ex

@pytest.fixture
def workflow_node_1(run_states,
                    mock_executable):
    workflow, _ = Workflow.objects.update_or_create(
        id=1,
        name='analyze',
        ingest_strategy_class='blue_sky.strategies.mock_ingest.MockIngest')
    job_queue, _ = JobQueue.objects.update_or_create(
        id=7,
        name='Mock Analyze',
        enqueued_object_class='blue_sky.models.observation.Observation',
        job_strategy_class='blue_sky.strategies.mock_analyze.MockAnalyze',
        executable=mock_executable,
        defaults={})
    w_node, _ = WorkflowNode.objects.update_or_create(
        id=1,
        defaults={
            'workflow': workflow,
            'job_queue': job_queue})

    return w_node


@pytest.fixture
def running_task_5(run_states,
                   mock_executable):
    workflow, _ = Workflow.objects.update_or_create(
        id=1)
    job_queue, _ = JobQueue.objects.update_or_create(
        id=7,
        executable=mock_executable,
        defaults={
            'job_strategy_class': 
            'workflow_engine.strategies.wait_strategy.WaitStrategy'})
    workflow_node, _ = WorkflowNode.objects.update_or_create(
        id=1,
        defaults={
            'workflow': workflow,
            'job_queue': job_queue})
    job, _ = Job.objects.update_or_create(
        id=2,
        defaults = {
            'enqueued_object_id': 56,
            'run_state': run_states['RUNNING'],
            'workflow_node': workflow_node,
            'start_run_time': timezone.now()})
    task, _ = Task.objects.update_or_create(
        id=5,
        job=job,
        defaults={
            'full_executable': 'mock_task',
            'run_state': run_states['RUNNING'],
            'start_run_time': timezone.now()})

    return task

# circular imports
from workflow_engine.models.task import Task
from workflow_engine.models.run_state import RunState
from workflow_engine.models.job import Job
from workflow_engine.models.job_queue import JobQueue
from workflow_engine.models.workflow_node import WorkflowNode
from workflow_engine.models.executable import Executable
from workflow_engine.models.workflow import Workflow
