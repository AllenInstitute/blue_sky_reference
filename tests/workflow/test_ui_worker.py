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
from workflow_engine.workflow_controller import WorkflowController
from workflow_engine.celery import signatures
from tests.signature_fixtures import (
    ENQUEUE_NEXT,
    mock_celery_task  # noqa # pylint: disable=unused-import
)
from tests.workflow.workflow_fixtures import (
    run_states,      # noqa # pylint: disable=unused-import
    task_5,          # noqa # pylint: disable=unused-import
    obs             # noqa # pylint: disable=unused-import
)


# Message queue fixtures
from tests.celery_fixtures import (
    celery_enable_logging,           # noqa # pylint: disable=unused-import
    celery_config,                   # noqa # pylint: disable=unused-import
    use_celery_app_trap,             # noqa # pylint: disable=unused-import
    celery_worker_parameters_helper,
    celery_includes_helper,
    workflow_celery_app,             # noqa # pylint: disable=unused-import
)


@pytest.fixture
def celery_includes():
    return celery_includes_helper(['workflow_engine.celery.workflow_tasks'])


@pytest.fixture
def celery_worker_parameters():
    return celery_worker_parameters_helper('workflow')



@pytest.mark.django_db(transaction=True)
@patch('workflow_engine.workflow_controller.run_workflow_node_jobs_signature')
def test_create_job(
    mock_start_helper,
    workflow_celery_app,
    celery_worker,
    task_5,
    obs):

    workflow_node_id = 1
    priority = 50

    num_jobs_before = Job.objects.count()

    result = signatures.create_job_signature.delay(
        workflow_node_id,
        obs.id,
        priority)

    assert not result.failed()

    job_id = result.wait(10)

    assert job_id > 0

    num_jobs_after = Job.objects.count()
    assert num_jobs_after == num_jobs_before + 1

# circular imports
from workflow_engine.models import Job
