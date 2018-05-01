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
from workflow_engine.models.run_state import RunState
from workflow_client.client_settings import configure_worker_app
from tests.nb_utils.test_moab_api \
    import moab_dict, task_status_dict_queued
from workflow_engine.celery.moab_tasks \
    import check_moab_status
from tests.workflow.workflow_fixtures \
    import run_states, task_5, running_task_5, obs, mock_executable
from django.test.utils import override_settings
from celery.contrib.pytest \
    import celery_app, celery_worker
from mock import Mock, patch
import time

_MOAB_ID_OFFSET = 20

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
        'queues': ( 'moab_blue_sky', 'result', 'null' )
    }


@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='session')
def celery_includes():
    return [
        'tests.workflow.test_moab_tasks'
    ]


@pytest.fixture
def mock_moab_result():
    return [ {
        'name': str(i),
        'id': 'Moab.' + (i + _MOAB_ID_OFFSET),
        'customName': 'task_' + str(i*10 + i),  # i needs to match an id in task data
        'states': { 'state': 'Running' },
        'credentials': { 'user': 'somebody' },
        'completionCode': 0
    } for i in [2, 4] ]


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    UI_HOST='example.org',
    UI_PORT=888,
    MOAB_MESSAGE_QUEUE_NAME='moab_blue_sky')
@pytest.mark.celery(task_cls='workflow_engine.celery.moab_tasks')
@patch('workflow_client.nb_utils.moab_api.moab_query')
def test_check_pbs_status(
    mock_moab_query,
    celery_app,
    celery_worker,
    task_5,
    moab_dict):
    mock_moab_query.return_value=moab_dict

    task_5.run_state = RunState.get_queued_state()
    task_5.pbs_id = 'Moab.' + str(task_5.id + _MOAB_ID_OFFSET)
    task_5.save()

    configure_worker_app(celery_app, 'blue_sky')

    result = check_moab_status.apply_async(
        queue='moab_blue_sky')

    r = result.wait(10)

    # see: http://docs.celeryproject.org/en/latest/reference/celery.result.html
    #result.wait(timeout=10)
    #print(r)
    #assert set(r) == {1, 2, 3, 4}

    mock_moab_query.assert_called()
