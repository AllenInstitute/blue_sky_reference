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
from workflow_engine.simple_router import SimpleRouter
from workflow_engine.client_settings import configure_worker_app
from tests.nb_utils.test_moab_api import (
    moab_dict,               # noqa # pylint: disable=unused-import
    task_status_dict_queued  # noqa # pylint: disable=unused-import
)
from workflow_engine.signatures import check_moab_status_signature
from tests.workflow.workflow_fixtures import (
    task_5,          # noqa # pylint: disable=unused-import
    running_task_5,  # noqa # pylint: disable=unused-import
    obs,             # noqa # pylint: disable=unused-import
    mock_executable  # noqa # pylint: disable=unused-import
)
from celery.contrib.pytest import (
    celery_app,    # noqa # pylint: disable=unused-import
    celery_worker  # noqa # pylint: disable=unused-import
)
from mock import patch
import os

_MOAB_ID_OFFSET = 20

@pytest.fixture(scope='module')
def celery_enable_logging():
    return True


@pytest.fixture(scope='module')
def celery_worker_parameters():
    router = SimpleRouter('blue_sky')

    return {
        'queues': ('moab_status@blue_sky', 'result@blue_sky', 'moab@blue_sky'),
        'task_routes': (router.route_task,),
        'perform_ping_check': False
    }


@pytest.fixture(scope='module')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='module')
def celery_includes():
    return [
        'workflow_engine.celery.moab_status_tasks',
        'tests.workflow.celery_signal_handlers'
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

@pytest.fixture
def moab_status_celery_app(celery_app):
    configure_worker_app(celery_app, 'blue_sky', 'moab_status')

    return celery_app

@pytest.mark.django_db(transaction=True)
@patch('workflow_engine.nb_utils.moab_api.moab_query')
def test_check_moab_status(
    mock_moab_query,
    moab_status_celery_app,
    celery_worker,
    task_5,
    moab_dict):
    mock_moab_query.return_value=moab_dict

    os.environ['MOAB_AUTH'] = 'moab_user:moab_password'

    task_5.pbs_id = 'Moab.' + str(task_5.id + _MOAB_ID_OFFSET)
    task_5.set_queued_state(quiet=True)

    result = check_moab_status_signature.clone(
        delivery_mode='persistent').delay()

    #r = result.wait(10)

    # see: http://docs.celeryproject.org/en/latest/reference/celery.result.html
    #result.wait(timeout=10)
    #print(r)
    #assert set(r) == {1, 2, 3, 4}

    #mock_moab_query.assert_called()
