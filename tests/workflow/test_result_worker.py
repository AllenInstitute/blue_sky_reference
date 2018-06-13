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
import django; django.setup()
import time
from django.test.utils import override_settings
from workflow_client.client_settings import configure_worker_app
from workflow_engine.celery.result_tasks import \
    process_finished_execution, process_failed_execution, process_running
from workflow_engine.celery.signatures import process_running_signature,\
    process_finished_execution_signature, process_failed_execution_signature
from datetime import timedelta
from django.utils import timezone
from mock import patch
from tests.workflow.workflow_fixtures \
    import run_states, task_5, \
    running_task_5, mock_executable
import simplejson as json


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
        'task_default_queue': 'result_blue_sky'
    }


@pytest.fixture(scope='module')
def celery_worker_parameters():
    return {
        'queues': ( 'workflow_blue_sky',
                    'result_blue_sky',
                    'moab_blue_sky',
                    'null' )
    }

@pytest.fixture(scope='module')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='module')
def celery_includes():
    return [
        'tests.workflow.test_result_worker',
        'tests.workflow.celery_signal_handlers'
    ]


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    RESULT_MESSAGE_QUEUE_NAME='result_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.workflow_tasks')
def test_process_running(
        celery_app,
        celery_worker,
        task_5):
    configure_worker_app(celery_app, 'blue_sky')

    result = process_running_signature.delay(5)
    outpt = result.wait(10)
    assert str(outpt) == 'set running for task 5'

    assert not result.failed()


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    RESULT_MESSAGE_QUEUE_NAME='result_blue_sky')
@pytest.mark.celery(task_cls='workflow_engine.celery.workflow_tasks')
def test_process_finished_execution(
        celery_app,
        celery_worker,
        running_task_5):
    configure_worker_app(celery_app, 'blue_sky')

    result = process_finished_execution_signature.delay(5)
    outpt = result.wait(10)
    assert outpt == 'set finished for task 5'

    assert not result.failed()


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    RESULT_MESSAGE_QUEUE_NAME='result_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.workflow_tasks')
def test_process_failed_execution_task_not_found(
        celery_app,
        celery_worker,
        running_task_5):
    configure_worker_app(celery_app, 'blue_sky')

    result = process_failed_execution_signature.delay(1)
    time.sleep(17)
    outpt = result.wait(1)
    assert outpt == 'Task 1 not found'

    assert not result.failed()


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    RESULT_MESSAGE_QUEUE_NAME='result_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.workflow_tasks')
def test_process_failed_execution_15_second_window(
        celery_app,
        celery_worker,
        running_task_5):
    configure_worker_app(celery_app, 'blue_sky')

    result = process_failed_execution_signature.delay(5)
    outpt = result.wait(10)
    assert outpt == 'Not failing execution for task 5 in 15 second window'

    assert not result.failed()

@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    RESULT_MESSAGE_QUEUE_NAME='result_blue_sky')
@patch('workflow_engine.strategies.wait_strategy.WaitStrategy.run_task')
@pytest.mark.celery(task_cls='workflow_client.workflow_tasks')
def test_process_failed_execution(
        mrt,
        celery_app,
        celery_worker,
        running_task_5):
    configure_worker_app(celery_app, 'blue_sky')
    running_task_5.start_run_time = timezone.now() - timedelta(minutes=20)
    running_task_5.save()

    result = process_failed_execution_signature.delay(5)
    outpt = result.wait(1)
    assert outpt == 'set failed execution for task 5'

    assert not result.failed()
