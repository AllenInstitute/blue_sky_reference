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
import workflow_engine.signatures as signatures

# Workflow Fixtures
from tests.workflow.workflow_fixtures import (
    task_5,               # noqa # pylint: disable=unused-import
    running_task_5,       # noqa # pylint: disable=unused-import
    mock_executable       # noqa # pylint: disable=unused-import
)


# Message queue fixtures
from tests.celery_fixtures import (
    celery_enable_logging,           # noqa # pylint: disable=unused-import
    use_celery_app_trap,             # noqa # pylint: disable=unused-import
    celery_worker_parameters_helper,
    celery_includes_helper,
    result_celery_app,               # noqa # pylint: disable=unused-import
)


# celery_includes issue workaround
from workflow_engine.celery.result_tasks import (
    process_running,             # noqa # pylint: disable=unused-import
    process_finished_execution,  # noqa # pylint: disable=unused-import
    process_failed_execution     # noqa # pylint: disable=unused-import
)

import logging
_log = logging.getLogger('test.workflow.test_result_worker')


@pytest.fixture
def celery_includes():
    return celery_includes_helper(['workflow_engine.celery.result_tasks'])


@pytest.fixture
def celery_worker_parameters():
    return celery_worker_parameters_helper('result')


@pytest.mark.django_db(transaction=True)
def test_process_running(
    result_celery_app,
    celery_worker,
    task_5):

    task_5.job.set_queued_state(quiet=True)
    task_5.set_queued_state(quiet=True)
    result = signatures.process_running_signature.delay(5)
    assert not result.failed()
    outpt = result.wait(10)
    assert str(outpt) == 'set running for task 5'


@pytest.mark.django_db(transaction=True)
def xtest_process_finished_execution(
    result_celery_app,
    celery_worker,
    running_task_5):

    result = signatures.process_finished_execution_signature.delay(5)
    outpt = result.wait(10)
    assert outpt == 'set finished for task 5'
 
    assert not result.failed()


@pytest.mark.django_db(transaction=True)
def xtest_process_failed_execution_task_not_found(
    result_celery_app,
    celery_worker,
    running_task_5):

    result = signatures.process_failed_execution_signature.delay(1)
    assert not result.failed()
    outpt = result.wait(10)
    assert outpt == 'Task 1 not found'


@pytest.mark.django_db(transaction=True)
def xtest_process_failed_execution_15_second_window(
    result_celery_app,
    celery_worker,
    running_task_5):

    result = signatures.process_failed_execution_signature.delay(5)
    outpt = result.wait(10)
 
    assert outpt == 'Not failing execution for task 5 in moab check window'
    assert not result.failed()
