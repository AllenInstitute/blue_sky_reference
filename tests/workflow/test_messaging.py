# Allen Institute Software License - This software license is the 2-clause BSD
# license plus a third clause that prohibits redistribution for commercial
# purposes without further permission.
#
# Copyright 2018. Allen Institute. All rights reserved.
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
from django.test.utils import override_settings
import time
import celery
from mock import Mock, patch
import shutil
from workflow_engine.models.job import Job
from tests.workflow.workflow_fixtures \
    import run_states, workflow_node_1, obs, mock_executable
from workflow_client.worker_client import create_job, run_server_command
from workflow_client.celery_run_consumer import run_workflow_node_jobs_by_id
from workflow_engine.celery.workflow_tasks \
    import process_running, process_finished_execution, \
    process_failed_execution, process_pbs_id
# TODO: stuff that requires moab worker
from tests.workflow.messaging_combined_cofiguration \
    import configure_combined_app
from celery.contrib.pytest import celery_app, celery_worker
import logging


_log = logging.getLogger('tests.workflow.test_messaging')


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
        'queues': ( 'workflow', 'pbs', 'result', 'null' )
    }

@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='session')
def celery_includes():
    return [
        'tests.workflow.test_messaging',
        'tests.workflow.celery_signal_handlers'
    ]

def mock_run_celery_task(args, *other_args, **kwargs):
    (full_executable, task_id, logfile, use_pbs) = args

    _log.info(
        'mock run_celery_task: '
        'full_executable=%s '
        'task_id=%d '
        'logfile=%s '
        'use_pbs=%s)',
        full_executable,
        task_id,
        logfile,
        str(use_pbs))
    process_running.apply_async(
            (task_id,),
            countdown=1,
            queue='result')
    task = Task.objects.get(id=task_id)
    shutil.copy(
        task.input_file,
        task.output_file)
    process_finished_execution.apply_async(
        (task_id,),
        countdown=2,
        queue='result')


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    PBS_MESSAGE_QUEUE_NAME='pbs',
    CELERY_MESSAGE_QUEUE_NAME='celery_blue_sky')
@pytest.mark.celery(task_cls='test.workflow.test_messaging')
def test_create_job(
        celery_app,
        celery_worker,
        workflow_node_1,
        obs):
    configure_combined_app(celery_app, 'blue_sky')

    workflow_node_id = 1
    priority = 50

    run_delay = 2,
    finished_delay = 3

    try:
        shutil.rmtree(
            'example_data/1/jobs/job_1/tasks/task_1/input_1.json',
            ignore_errors=True)
    except Exception as e:
        _log.error(str(e))

    run_celery_task_async_mock = Mock(
        return_value=('', ''),
        side_effect=mock_run_celery_task)

    with patch(
        'workflow_client.worker_client.run_celery_task.apply_async',
        run_celery_task_async_mock):
        result = create_job.apply_async(
            (workflow_node_id,
             obs.id,
             priority),
            queue='workflow')
        time.sleep(10)
        created_job_id = result.get()

    assert not result.failed()

    updated_task = Task.objects.get(
        job_id=created_job_id)
    assert updated_task.run_state.id == \
        RunState.objects.get(name='SUCCESS').id
    run_celery_task_async_mock.assert_called()


# circular imports
from workflow_engine.models.task import Task
from workflow_engine.models.run_state import RunState

