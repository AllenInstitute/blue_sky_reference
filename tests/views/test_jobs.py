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
from workflow_engine.views import job_view


@pytest.fixture
def rf():
    return django.test.RequestFactory()

@pytest.mark.django_db(transaction=True)
def test_job(rf):
    request = rf.get('/workflow_engine/jobs')
    response = job_view.jobs(request)
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_jobs_page(rf):
    request = rf.get('/workflow_engine/jobs/2')
    response = job_view.jobs_page(request, 2)
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_queue_job(rf):
    request = rf.get('/workflow_engine/jobs/2')
    response = job_view.queue_job(request)
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_kill_job(rf):
    request = rf.get('/workflow_engine/jobs/2')
    response = job_view.kill_job(request)
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_get_job_status(rf):
    job_id = 2
    request = rf.get('/workflow_engine/jobs/{}'.format(job_id))
    response = job_view.get_job_status(request)
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_get_job_show_data(rf):
    request = rf.get('/workflow_engine/jobs/2')
    response = job_view.get_job_show_data(request)
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_run_all_jobs(rf):
    request = rf.get('/workflow_engine/jobs/2')
    response = job_view.run_all_jobs(request)
    assert response.status_code == 200