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
import time
from django.test.utils import override_settings
from workflow_client.client_settings import configure_worker_app
from workflow_engine.celery.result_tasks import (
    process_finished_execution,
    process_failed_execution,
    process_running
)
from workflow_engine.strategies.execution_strategy import ExecutionStrategy
from workflow_engine.celery.signatures import (
    process_running_signature,
    process_finished_execution_signature,
    process_failed_execution_signature
)
from workflow_client.simple_router import SimpleRouter
from datetime import timedelta
from django.utils import timezone
from tests.workflow.workflow_fixtures import (
    task_5,
    running_task_5,
    mock_executable
)
import logging
import os

_log = logging.getLogger('test.workflow.test_result_worker')


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
        'queues': ('result_blue_sky',),
        'task_routes': (router.route_task,),
        'perform_ping_check': False
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

@pytest.fixture
@patch('workflow_client.client_settings.get_message_broker_url',
        Mock(return_value='memory://'))
def result_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'result')

    return celery_app

@pytest.fixture
def result_celery_worker(celery_worker):
    return celery_worker


@pytest.mark.skipif(
    os.environ.get('INCLUDE_PROBLEM_TESTS') != 'true',
    reason='these tests conflict when run with the full suite')
@pytest.mark.django_db
def test_process_failed_execution(
        result_celery_app,
        result_celery_worker,
        running_task_5):
    running_task_5.start_run_time = timezone.now() - timedelta(minutes=20)
    running_task_5.save()
 
    with patch.object(
        ExecutionStrategy,
        'set_error_message_from_log'
    ):
        result = process_failed_execution_signature.delay(5)
        outpt = result.wait(1)
  
        assert outpt == 'set failed execution for task 5'
        assert not result.failed()
