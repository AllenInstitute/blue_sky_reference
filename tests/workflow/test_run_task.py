# Allen Institute Software License - This software license is the 2-clause BSD
# license plus a third clause that prohibits redistribution for commercial
# purposes without further permission.
#
# Copyright 2017. Allen Institute. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Redistributions for commercial purposes are not permitted without the
# Allen Institute's written permission.
# For purposes of this license, commercial purposes is the incorporation of the
# Allen Institute's software into anything for which you will charge fees or
# other compensation. Contact terms@alleninstitute.org for commercial licensing
# opportunities.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import pytest
from django.utils.timezone import now
from datetime import timedelta
from workflow_engine.models.task import Task
from workflow_engine.models.run_state import RunState
from workflow_engine.models.job import Job
from workflow_engine.models.job_queue import JobQueue
from workflow_engine.models.workflow_node import WorkflowNode
from workflow_engine.models.workflow import Workflow
from django.test.utils import override_settings
import time
from workflow_client.celery_run_consumer \
    import run_task, success, fail, configure_run_app


@pytest.fixture(scope='session')
def celery_enable_logging():
    return True


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc',
        'task_default_exchange': 'blue_sky',
        'task_default_routing_key': 'result',
        'task_default_queue': 'result'
    }


@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'queues': ( 'run', 'result', 'null' )
    }


@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='session')
def celery_includes():
    return [
        'workflow_client.celery_run_consumer'
    ]


def get_timeout_eta(timeout_seconds):
    return now() + timedelta(seconds=timeout_seconds)

@pytest.fixture
def task_5():
    pending, _ = RunState.objects.update_or_create(name='PENDING')
    running, _ = RunState.objects.update_or_create(name='RUNNING')
    failed_ex, _ = RunState.objects.update_or_create(name='FAILED_EXECUTION')
    failed, _ = RunState.objects.update_or_create(name='FAILED')

    workflow, _ = Workflow.objects.update_or_create(
        id=1)
    job_queue, _ = JobQueue.objects.update_or_create(
        id=7,
        defaults={
            'job_strategy_class': 'workflow_engine.strategies.base_strategy.BaseStrategy'})
    workflow_node, _ = WorkflowNode.objects.update_or_create(
        id=1,
        defaults={
            'workflow': workflow,
            'job_queue': job_queue})
    job, _ = Job.objects.update_or_create(
        id=2,
        defaults = {
            'enqueued_object_id': 56,
            'run_state_id': pending.id,
            'workflow_node': workflow_node})
    task, _ = Task.objects.update_or_create(
        id=5,
        job=job,
        defaults={
            'full_executable': 'mock_task',
            'run_state_id': pending.id})

    return task

@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    PBS_MESSAGE_QUEUE_NAME='run', # TODO: not PBS QUEUE
    CELERY_MESSAGE_QUEUE_NAME='celery_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.celery_run_consumer')
def test_run_task(celery_app,
                  celery_worker):
    configure_run_app(celery_app, 'blue_sky')
    def assert_false():
        assert False
    def assert_true():
        assert True

    result = run_task.apply_async(
        ('echo', 'whatever'),
        queue='run',
        link=success.s(),
        link_error=fail.s()
        )
    time.sleep(10)
    outpt = result.get()

    assert not result.failed()
