# Allen Institute Software License - This software license is the 2-clause BSD
# license plus a third clause that prohibits redistribution for commercial
# purposes without further permission.
#
# Copyright 2018-2019. Allen Institute. All rights reserved.
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
import workflow_client.signatures as signatures
from blue_sky.models.observation import Observation

from tests.workflow.workflow_fixtures import (
    workflow_node_1, # noqa # pylint: disable=unused-import
    task_5,          # noqa # pylint: disable=unused-import
    running_task_5,  # noqa # pylint: disable=unused-import
    mock_executable  # noqa # pylint: disable=unused-import
)
from workflow_engine.celery.ingest_tasks import (
    ingest_task  # noqa # pylint: disable=unused-import
)

# Message queue fixtures
from tests.celery_fixtures import (
    celery_enable_logging,           # noqa # pylint: disable=unused-import
    use_celery_app_trap,             # noqa # pylint: disable=unused-import
    celery_worker_parameters_helper,
    celery_includes_helper,
    ingest_celery_app,             # noqa # pylint: disable=unused-import
)


@pytest.fixture
def celery_includes():
    return celery_includes_helper(['workflow_engine.celery.ingest_tasks'])


@pytest.fixture
def celery_worker_parameters():
    return celery_worker_parameters_helper('ingest')


@pytest.mark.django_db(transaction=True)
def test_ingest(
        ingest_celery_app,
        celery_worker,
        workflow_node_1):
    message = {
        'arg1': 5,
        'arg2': "Whatever",
        'arg3': "Something"
    }

    tags = ['observation']

    result = signatures.ingest_signature.delay('analyze', message, tags)
    assert not result.failed()

    response_message = result.wait(10)

    obs_id = response_message["observation_id"]
    new_observation = Observation.objects.get(id=obs_id)
    assert new_observation is not None

