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
from mock import Mock, patch
from celery.contrib.pytest import celery_app, celery_worker
import shutil
from workflow_engine.celery.signatures import (
    process_running_signature,
    process_finished_execution_signature,
    create_job_signature
)
from workflow_client.simple_router import SimpleRouter
import time
from workflow_client.client_settings import configure_worker_app
from tests.workflow.workflow_fixtures import (
    run_states,
    workflow_node_1,
    obs,
    mock_executable
)
import logging


_log = logging.getLogger('tests.workflow.test_messaging')


@pytest.fixture(scope='module')
def celery_enable_logging():
    return True

@pytest.fixture(scope='module')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc'
    }


@pytest.fixture(scope='module')
def celery_worker_parameters():
    router = SimpleRouter('blue_sky')

    return {
        'queues': ( 'workflow_blue_sky',
                    #'moab_blue_sky',   # hook up mock moab worker
                    'result_blue_sky', ),
        'task_routes': (router.route_task,),
        'perform_ping_check': False
    }

@pytest.fixture(scope='module')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='module')
def celery_includes():
    return [
        #'tests.workflow.test_messaging',
        #'workflow_engine.celery.moab_tasks',
        'workflow_engine.celery.workflow_tasks',
        'workflow_engine.celery.result_tasks',
        'tests.workflow.celery_signal_handlers'
    ]

def send_running_and_finished(arg_tuple, queue, link):
    task_id = arg_tuple[0]

    _log.info(
        'task id: %d',
        task_id)
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


_mock_submit_job = Mock(
    name='mock_submit_moab_task')
_mock_submit_job.apply_async = Mock(
    return_value={ 'name': 'MockMoab:15' },
    side_effect=send_running_and_finished)

@pytest.fixture
@patch('workflow_client.client_settings.get_message_broker_url',
        Mock(return_value='memory://'))
def combined_celery_app(celery_app):
    configure_worker_app(
        celery_app,
        'blue_sky',
        worker_names=['workflow', 'result']) #, 'moab']) # hook up mock moab worker

    return celery_app


#@pytest.mark.xfail
@pytest.mark.django_db
#@patch('workflow_engine.celery.signatures.run_workflow_node_jobs_signature')
#@patch('workflow_engine.celery.signatures.enqueue_next_queue_signature')
#@patch('workflow_engine.celery.moab_tasks.submit_moab_task', _mock_submit_job)
def test_create_job(
        #mock_enqueue_next_queue,
        combined_celery_app,
        celery_worker,
        workflow_node_1,
        obs):
    #mock_enqueue_next_queue.delay = Mock()

    workflow_node_id = workflow_node_1.id
    priority = 50

    try:
        shutil.rmtree(
            'example_data/1/jobs/job_1/tasks/task_1/input_1.json',
            ignore_errors=True)
    except Exception as e:
        _log.error(str(e))

    result = create_job_signature.delay(
        workflow_node_id,
        obs.id,
        priority)

    created_job_id = result.wait(10)
    #_mock_submit_job.delay.assert_called_once()
    assert not result.failed()
    assert created_job_id == -1

    #raise Exception(created_job_id)

    #updated_task = Task.objects.get(
    #    job_id=created_job_id)
    #assert (updated_task.run_state.id == 
    #    RunState.objects.get(name='SUCCESS').id)
    #menqn.delay.assert_called_once_with(workflow_node_1.id)


# circular imports
from workflow_engine.models.task import Task
from workflow_engine.models.run_state import RunState

