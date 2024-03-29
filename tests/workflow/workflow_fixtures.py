import pytest
from django.utils import timezone
from workflow_engine.mixins import Runnable
from blue_sky.models.observation import Observation
from django.contrib.contenttypes.models import ContentType


@pytest.fixture
def obs():
    (o, _) = Observation.objects.update_or_create(
        arg1='5',
        arg2='Whatever',
        arg3='Something',
        object_state='PROCESSING')

    return o


@pytest.fixture
def waiting_task():
    workflow, _ = Workflow.objects.update_or_create(
        id=1,
        name="analyze",
        ingest_strategy_class='blue_sky.strategies.mock_ingest.MockIngest')
    job_queue, _ = JobQueue.objects.update_or_create(
        id=8,
        name='Mock Wait',
        enqueued_object_type = ContentType.objects.get_for_model(Observation),
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
        object_state='CONTEMPLATIVE')
    job, _ = Job.objects.update_or_create(
        id=9,
        defaults = {
            'enqueued_object': waiter_obs,
            'running_state': Runnable.STATE.PENDING,
            'workflow_node': workflow_node})

    return job


@pytest.fixture
def task_5():
    xcute,_ = Executable.objects.get_or_create(
        name='Mock Executable',
        defaults={
            'description': 'Mock',
            'executable_path': '/lorem/ipsum',
            'static_arguments': None,
            'environment': '',
            'remote_queue': 'pbs',
            'pbs_queue': 'NULLQUEUE',
            'pbs_processor': 'ERROR',
            'pbs_walltime': 'ERROR'})
    workflow, _ = Workflow.objects.update_or_create(
        id=1,
        name="analyze",
        ingest_strategy_class='blue_sky.strategies.mock_ingest.MockIngest')
    obs = Observation(id=56)
    obs.save()
    job_queue, _ = JobQueue.objects.update_or_create(
        id=7,
        name='Mock Analyze',
        enqueued_object_type = ContentType.objects.get_for_model(Observation),
        job_strategy_class='blue_sky.strategies.mock_analyze.MockAnalyze',
        executable=xcute,
        defaults={})
    workflow_node, _ = WorkflowNode.objects.update_or_create(
        id=1,
        defaults={
            'workflow': workflow,
            'job_queue': job_queue})
    job, _ = Job.objects.update_or_create(
        id=2,
        defaults = {
            'enqueued_object_id': obs.id,
            'running_state': Runnable.STATE.PENDING,
            'workflow_node': workflow_node})
    task, _ = Task.objects.update_or_create(
        id=5,
        job=job,
        defaults={
            'enqueued_task_object_id': obs.id,
            'full_executable': 'mock_task',
            'running_state': Runnable.STATE.PENDING,
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
def workflow_node_1(mock_executable):
    workflow, _ = Workflow.objects.update_or_create(
        id=1,
        name='analyze',
        ingest_strategy_class='blue_sky.strategies.mock_ingest.MockIngest')
    job_queue, _ = JobQueue.objects.update_or_create(
        id=7,
        name='Mock Analyze',
        enqueued_object_type = ContentType.objects.get_for_model(Observation),
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
def running_task_5(mock_executable):
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
            'running_state': Runnable.STATE.RUNNING,
            'workflow_node': workflow_node,
            'start_run_time': timezone.now()})
    task, _ = Task.objects.update_or_create(
        id=5,
        job=job,
        defaults={
            'full_executable': 'mock_task',
            'running_state': Runnable.STATE.RUNNING,
            'start_run_time': timezone.now()})

    return task

# circular imports
from workflow_engine.models import (
    Task,
    Job,
    JobQueue,
    WorkflowNode,
    Executable,
    Workflow,
)
