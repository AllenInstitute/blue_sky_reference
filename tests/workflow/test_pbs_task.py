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
from workflow_client.celery_pbs_consumer import run_pbs,\
    configure_pbs_consumer_app, fail, on_raw_message, success, check_pbs_status
from celery.app import shared_task
from mock import Mock, patch
import time
from celery.result import ResultBase
from celery.contrib.pytest \
    import celery_session_app, celery_session_worker

@pytest.fixture(scope='session')
def celery_enable_logging():
    return True

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc'
    }

@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True

@pytest.fixture(scope='session')
def celery_includes():
    return [
        'tests.workflow.test_pbs_task'
    ]

@shared_task
def mul(x, y):
    return x * y

#@pytest.mark.celery(task_cls='workflow_client.celery_pbs_consumer')
def test_mul_task(celery_session_app,
                  celery_session_worker):
#     configure_pbs_consumer_app(
#         celery_session_app,
#         'at_em_imaging_workflow')

    result = mul.apply_async((2, 3))
    outpt = result.get()

    assert outpt == 6


def test_run_task(celery_session_app,
                  celery_session_worker):
#     configure_pbs_consumer_app(
#         celery_session_app,
#         'at_em_imaging_workflow')

    mock_on_raw_message = Mock()

    result = run_pbs.apply_async(
        link=success.s(),
        link_error=fail.s())
    outpt = result.get(
        on_message=mock_on_raw_message,
        propagate=False)

    mock_on_raw_message.assert_called()
    assert  outpt == 'OK'


def test_check_pbs_status(
    celery_session_app,
    celery_session_worker):
#     configure_pbs_consumer_app(
#         celery_session_app,
#         'at_em_imaging_workflow')
    with patch(
        'workflow_client.celery_pbs_consumer.on_pbs_running',
        Mock(return_value="MOCK RUNNING")) as pbsf:
        result = check_pbs_status.apply_async()

        # see: http://docs.celeryproject.org/en/latest/reference/celery.result.html
        for r in result.collect():
            if not isinstance(r, (ResultBase, tuple)):
                assert r == 'MOCK RUNNING'

#         @celery_session_app.on_after_configure.connect
#         def setup_periodic_tasks(sender, **kwargs):
#             sender.add_periodic_task(
#                 1.0,
#                 check_pbs_status.s(),
#                 name='Check PBS Status',
#                 expires=10)

    time.sleep(20)
    pbsf.assert_called()
