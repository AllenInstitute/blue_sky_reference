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
from workflow_client.simple_router import SimpleRouter
from mock import Mock, patch, call
from celery.contrib.pytest import celery_app, celery_worker
from workflow_client.client_settings import configure_worker_app
from workflow_engine.celery.signatures import create_job_signature
# from workflow_engine.celery.workflow_tasks import (
#     run_workflow_node_jobs_by_id,
#     create_job,
#     queue_job
# )
from tests.workflow.workflow_fixtures import (
    run_states,
    task_5,
    running_task_5,
    obs
)


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
        'queues': ('workflow_blue_sky','result_blue_sky'),
        'task_routes': (router.route_task,),
        'perform_ping_check': False
    }

@pytest.fixture(scope='module')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='module')
def celery_includes():
    return [
        'workflow_engine.celery.workflow_tasks',
        'tests.workflow.celery_signal_handlers'
    ]


@pytest.fixture
@patch('workflow_client.client_settings.get_message_broker_url',
        Mock(return_value='memory://'))
def workflow_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'workflow')

    return celery_app

@pytest.mark.xfail
@pytest.mark.django_db
#@pytest.mark.celery(task_cls='workflow_engine.celery.workflow_tasks')
# @patch(
#    'workflow_engine'
#    '.celery'
#    '.run_tasks'
#    '.run_workflow_node_jobs_by_id'
#    '.apply_async')
def test_create_job(
        #run_job_mock,
        workflow_celery_app,
        celery_worker,
        task_5,
        obs):
    #print('FN: ' + str(run_workflow_node_jobs_by_id))
    workflow_node_id = 1
    priority = 50

    num_jobs_before = Job.objects.count()

    result = create_job_signature.delay(
        workflow_node_id,
        obs.id,
        priority)

    outpt = result.wait(10)
#     run_job_mock.assert_called_once_with(
#         (1,),
#         {},
#         broker_connection_retry=False,
#         broker_connection_timeout=10,
#         queue='workflow_blue_sky')

    num_jobs_after = Job.objects.count()
    assert num_jobs_after == num_jobs_before + 1

    assert not result.failed()


# circular imports
from workflow_engine.models.job import Job
