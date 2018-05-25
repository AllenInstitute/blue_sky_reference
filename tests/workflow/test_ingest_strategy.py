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
from celery.contrib.pytest import celery_app, celery_worker
import time
from django.test.utils import override_settings
from workflow_client.client_settings import configure_worker_app
from workflow_engine.celery.ingest_tasks import ingest_task
from blue_sky.models.observation import Observation
from tests.workflow.workflow_fixtures \
    import run_states, workflow_node_1, task_5, \
    running_task_5, mock_executable


@pytest.fixture(scope='module')
def celery_enable_logging():
    return True


@pytest.fixture(scope='module')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc',
        'task_default_exchange': 'blue_sky',
        'task_default_routing_key': 'result',
        'task_default_queue': 'result'
    }


@pytest.fixture(scope='module')
def celery_worker_parameters():
    return {
        'queues': ( 'ingest', 'workflow', 'result', 'null' )
    }


@pytest.fixture(scope='module')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='module')
def celery_includes():
    return [
        'workflow_engine.celery.ingest_tasks',
        'tests.workflow.celery_signal_handlers'
    ]


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    INGEST_MESSAGE_QUEUE_NAME='ingest',
    RESULT_MESSAGE_QUEUE_NAME='result')
@pytest.mark.celery(task_cls='workflow_engine.celery.ingest_tasks')
def test_ingest(
        celery_app,
        celery_worker,
        workflow_node_1,):
    configure_worker_app(celery_app, 'blue_sky')

    message = {
        'arg1': 5,
        'arg2': "Whatever",
        'arg3': "Something"
    }

    tags = ['sunday']

    result = ingest_task.apply_async(
        ('analyze', message, tags),
        queue='ingest')
    assert not result.failed()

    response_message = result.wait(10)

    obs_id = response_message["observation_id"]
    new_observation = Observation.objects.get(id=obs_id)
    assert new_observation is not None

