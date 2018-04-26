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
import celery
from mock import Mock, patch
import shutil
from workflow_engine.celery.signatures import process_running_signature,\
    process_finished_execution_signature, create_job_signature
import time
from tests.workflow.messaging_combined_configuration \
    import configure_combined_app
from tests.workflow.workflow_fixtures \
    import run_states, workflow_node_1, obs, mock_executable
from workflow_engine.celery.worker_tasks import create_job
from workflow_engine.celery.result_tasks \
    import process_running, process_finished_execution
from workflow_engine.workflow_controller import WorkflowController
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
        'task_default_queue': 'result_blue_sky'
    }


@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'queues': ( 'workflow_blue_sky',
                    'moab_blue_sky',
                    'result_blue_sky',
                    'null' )
    }

@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='session')
def celery_includes():
    return [
        'tests.workflow.test_messaging',
        'tests.workflow.celery_signal_handlers',
        'workflow_engine.celery.moab_tasks'

    ]

def send_running_and_finished(task_id, pbs_file):
    _log.info(
        'task id: %d'
        'pbs_file=%s ',
        task_id,
        pbs_file)
    process_running_signature.apply_async(
        (task_id,),
        countdown=1)
    task = Task.objects.get(id=task_id)
    shutil.copy(
        task.input_file,
        task.output_file)
    process_finished_execution_signature.apply_async(
        (task_id,),
        countdown=2)


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    MOAB_MESSAGE_QUEUE_NAME='moab_blue_sky',
    WORKFLOW_MESSAGE_QUEUE_NAME='workflow_blue_sky',
    RESULT_MESSAGE_QUEUE_NAME='result_blue_sky')
@pytest.mark.celery(task_cls='test.workflow.test_messaging')
@patch.object(WorkflowController, 'enqueue_next_queue')
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

    mock_submit_job = Mock(
        name='mock_submit_moab_task_signature',
        return_value={ 'name': 'MockMoab:15' },
        side_effect=send_running_and_finished)

    with patch(
        'workflow_engine.celery.moab_tasks.submit_job',
        mock_submit_job):
        result = create_job_signature.delay(
            workflow_node_id,
            obs.id,
            priority)

        created_job_id = result.wait(10)
        time.sleep(10)
        mock_submit_job.assert_called()
        assert not result.failed()
    
        updated_task = Task.objects.get(
            job_id=created_job_id)
        assert updated_task.run_state.id == \
            RunState.objects.get(name='SUCCESS').id


# circular imports
from workflow_engine.models.task import Task
from workflow_engine.models.run_state import RunState

