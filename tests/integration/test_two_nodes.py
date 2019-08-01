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
from mock import Mock, patch, mock_open
from django.test import Client
from django.contrib.auth.models import User
from celery.contrib.pytest import celery_app, celery_worker
import shutil
import os
from workflow_engine.celery import signatures
from workflow_client.tasks import circus_signatures
from tests.workflow_configurations import (
    TEST_CONFIG_YAML_TWO_NODES,
)
from workflow_client.client_settings import configure_worker_app
from tests.workflow.workflow_fixtures import (
    run_states,      # noqa # pylint: disable=unused-import
    workflow_node_1, # noqa # pylint: disable=unused-import
    obs,             # noqa # pylint: disable=unused-import
    mock_executable  # noqa # pylint: disable=unused-import
)
from workflow_engine.workflow_config import WorkflowConfig
from workflow_engine.models import (
    Configuration,
    Job,
    WorkflowNode
)
# Message queue fixtures
from tests.celery_fixtures import (
    celery_enable_logging,           # noqa # pylint: disable=unused-import
    celery_config,                   # noqa # pylint: disable=unused-import
    use_celery_app_trap,             # noqa # pylint: disable=unused-import
    celery_includes_helper,
    ingest_celery_app,             # noqa # pylint: disable=unused-import
)
# from workflow_engine.celery.mock_tasks import (
#     submit_mock_task
# )

import logging
from workflow_client.simple_router import SimpleRouter


_log = logging.getLogger('tests.integration.test_two_nodes')


@pytest.fixture
def celery_worker_parameters():
    router = SimpleRouter('blue_sky')

    queues = [ 'ingest@blue_sky', 'workflow@blue_sky', 'mock@blue_sky', 'result@blue_sky' ]

    return {
        'queues': queues,
        'router': (router.route_task,),
        'perform_ping_check': False
    }


@pytest.fixture
def celery_includes():
    return celery_includes_helper([
        'workflow_engine.celery.workflow_tasks',
        'workflow_engine.celery.mock_tasks',
        'workflow_engine.celery.result_tasks',
        'workflow_engine.celery.ingest_tasks',
    ])


@pytest.fixture
@patch('workflow_client.client_settings.get_message_broker_url',
        Mock(return_value='memory://'))
def combined_celery_app(
    celery_app,
    run_states):
    configure_worker_app(
        celery_app,
        'blue_sky',
        worker_names=['ingest', 'mock', 'workflow', 'result']) #, 'moab']) # hook up mock moab worker

    return celery_app


@pytest.mark.django_db
def test_send_ingest(
    combined_celery_app,
    celery_worker):
    yaml_text = TEST_CONFIG_YAML_TWO_NODES

    with patch("builtins.open",
        mock_open(read_data=yaml_text)):
        WorkflowConfig.create_workflow(
            os.path.join(os.path.dirname(__file__),
                         'dev.yml'))

    node = WorkflowNode.objects.first()

    json_dict = {
        'this': 'that'
    }

    config = Configuration(
        content_object=node,
        name='Test Configuration',
        configuration_type='Example Configuration',
        json_object=json_dict)
    config.save()

    conf = node.configurations.first()

    assert conf.name == 'Test Configuration'
    assert set(conf.json_object.keys()) == { 'this' }

    usr = User.objects.create_user(
        'test_user', 'test@example.org', 'test_pass')

    client = Client()
    client.force_login(usr)

    #response = client.get('/admin/workflow_engine/executable/')

    #assert response.status_code == 200

#     submit_response = circus_signatures.submit_mock_signature.clone((5,)).delay()
#     o = submit_response.wait(10)
#     _log.info(o)

    ingest_response = signatures.ingest_signature.delay(
        'test_workflow',
        {
            'arg1': 987,
            'arg2': 'Roger',
            'arg3': 'Wilco'
        },
        None
    )

    outpt = ingest_response.wait(10)

    assert 'observation_id' in outpt and outpt['observation_id'] > 0

    _log.info(outpt)

    # _log.info(combined_celery_app.control.inspect().stats())
    _log.info(combined_celery_app.control.inspect().registered_tasks())
    _log.info(combined_celery_app.control.inspect().active_queues())

    assert outpt is not None

    assert Job.objects.order_by('id').last().running_state == 'SUCCESS'
#     assert outpt == 'None'
#  
#     assert False


@pytest.mark.django_db
def xtest_create_job(
        #mock_enqueue_next_queue,
        combined_celery_app,
        celery_worker,
        workflow_node_1,
        obs):
    #mock_enqueue_next_queue.delay = Mock()

    workflow_node_id = workflow_node_1.id
    priority = 50

    try:
        shutil.rmtree(
            'example_data/1/jobs/job_1/tasks/task_1/input_1.json',
            ignore_errors=True)
    except Exception as e:
        _log.error(str(e))

    result = signatures.create_job_signature.delay(
        workflow_node_id,
        obs.id,
        priority)

    created_job_id = result.wait(10)

    #_mock_submit_job.delay.assert_called_once()
    assert not result.failed()
    assert created_job_id == -1

    #raise Exception(created_job_id)

    #updated_task = Task.objects.get(
    #    job_id=created_job_id)
    #assert (updated_task.run_state.id == 
    #    RunState.objects.get(name='SUCCESS').id)
    #menqn.delay.assert_called_once_with(workflow_node_1.id)

