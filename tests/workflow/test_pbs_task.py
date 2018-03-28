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
from workflow_client.celery_pbs_tasks import run_pbs,\
    fail, success, check_pbs_status, configure_pbs_app
from django.test.utils import override_settings
from celery.contrib.pytest \
    import celery_app, celery_worker
from mock import Mock, patch
import time


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
        'queues': ( 'pbs', 'result', 'null' )
    }


@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='session')
def celery_includes():
    return [
        'tests.workflow.test_pbs_task'
    ]


def test_run_task(celery_app,
                  celery_worker):
    mock_on_raw_message = Mock()

    result = run_pbs.apply_async(
        link=success.s(),
        link_error=fail.s())
    outpt = result.get(
        on_message=mock_on_raw_message,
        propagate=False)

    mock_on_raw_message.assert_called()
    assert  outpt == 'OK'


@pytest.fixture
def workflow_engine_task_data():
    return """id,run_state,start_run_time,end_run_time,duration,pbs_id
1,11,2008-07-06T05:04:03,2009-08-07T06:05:04,09:08:07,11
2,11,2008-07-06T05:04:03,2009-08-07T06:05:04,09:08:07,22
3,11,2008-07-06T05:04:03,2009-08-07T06:05:04,09:08:07,33
4,11,2008-07-06T05:04:03,2009-08-07T06:05:04,09:08:07,44
""".encode('utf-8')


@pytest.fixture
def mock_moab_result():
    return [ {
        'name': str(i),
        'customName': 'task_' + str(i*10 + i),  # i needs to match an id in task data
        'states': { 'state': 'Running' },
        'credentials': { 'user': 'somebody' }
    } for i in [2, 4] ]


@override_settings(
    APP_PACKAGE='blue_sky',
    UI_HOST='example.org',
    UI_PORT=888,
    PBS_MESSAGE_QUEUE_NAME='pbs',
    CELERY_MESSAGE_QUEUE_NAME='celery_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.celery_pbs_tasks')
def test_check_pbs_status(
    celery_app,
    celery_worker,
    workflow_engine_task_data,
    mock_moab_result):
    with patch(
        'workflow_client.nb_utils.moab_api.moab_query',
        Mock(return_value=mock_moab_result)) as pbsf:
        with patch('workflow_client.nb_utils.task_monitor.request_task_json',
                   Mock(return_value=workflow_engine_task_data)):
            configure_pbs_app(celery_app, 'blue_sky')

            result = check_pbs_status.apply_async(
                exchange='blue_sky',
                queue='pbs')

            while not result.ready():
                time.sleep(1)

            # see: http://docs.celeryproject.org/en/latest/reference/celery.result.html
            time.sleep(10)
            r = list(result.get())
            print(r)
            #assert set(r) == {1, 2, 3, 4}

    pbsf.assert_called()
