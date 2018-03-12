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
import django.test
from workflow_engine.views import workflow_view
import simplejson as json
from django.utils.six import BytesIO


@pytest.fixture
def rf():
    return django.test.RequestFactory()

@pytest.mark.django_db
def test_workflows(rf):
    request = rf.get('/workflow_engine/workflows')
    response = workflow_view.workflows(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_workflow_run_jobs(rf):
    request = rf.get('/workflow_engine/workflows/run_jobs')
    response = workflow_view.run_jobs(request)
    assert response.status_code == 200
    json_data = json.load(BytesIO(response.content))
    assert json_data['success'] is False


@pytest.mark.django_db
def test_get_workflow_status(rf):
    request = rf.get('/workflow_engine/workflows')
    response = workflow_view.get_workflow_status(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_head_workflow_node_id(rf):
    request = rf.get('/workflow_engine/workflows')
    response = workflow_view.get_head_workflow_node_id(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_node_info(rf):
    request = rf.get('/workflow_engine/workflows')
    response = workflow_view.get_node_info(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_workflow_node(rf):
    request = rf.get('/workflow_engine/workflows')
    response = workflow_view.update_workflow_node(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_workflow_info(rf):
    request = rf.get('/workflow_engine/workflows')
    response = workflow_view.get_workflow_info(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_workflow(rf):
    request = rf.get('/workflow_engine/workflows')
    response = workflow_view.update_workflow(request)
    assert response.status_code == 200