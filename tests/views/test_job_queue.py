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
from mock import patch, mock_open
import django.test
from workflow_engine.views import job_queue_view
from workflow_engine.workflow_config import WorkflowConfig
from tests.workflow_configurations import TEST_CONFIG_YAML_TWO_NODES
import simplejson as json
import os
from workflow_engine.models.job_queue import JobQueue


@pytest.fixture
def rf():
    return django.test.RequestFactory()

def content_payload_to_dict(r):
    payload = json.loads(
        r.content)['payload']
    del payload['order_length']
    p2 = {}
    for elem in payload.values():
        p2.update(elem)

    return p2


@pytest.mark.django_db
def test_job_queues_show_data(rf):
    yaml_text = TEST_CONFIG_YAML_TWO_NODES

    with patch("builtins.open",
        mock_open(read_data=yaml_text)):
        WorkflowConfig.create_workflow(
            os.path.join(os.path.dirname(__file__),
                         'dev.yml'))

    jq_id = JobQueue.objects.first().id

    request = rf.get(
        '/workflow_engine/jobs?job_queue_id=%d' %(
            jq_id))
    response = job_queue_view.get_job_queues_show_data(request)
    assert response.status_code == 200

    payload = content_payload_to_dict(response)

    assert set(payload.keys()) == set([
        'name', 'executable name', 'job strategy class',
        'executable path', 'id', 'updated at', 'created at',
        'description', 'enqueued object type'])


@pytest.mark.django_db
def test_job_queues(rf):
    request = rf.get('/workflow_engine/jobs')
    response = job_queue_view.job_queues(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_job_queues_page(rf):
    request = rf.get('/workflow_engine/jobs')
    page = 2
    response = job_queue_view.job_queues_page(request, page)
    assert response.status_code == 200
