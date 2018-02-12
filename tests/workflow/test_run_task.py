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
from mock import patch, mock_open, Mock, MagicMock
import os
from time import sleep
from django.utils.timezone import now
from datetime import timedelta
from billiard.exceptions import SoftTimeLimitExceeded
from workflow_engine.models.task import Task
from workflow_engine.models.run_state import RunState
from workflow_engine.models.job import Job
from workflow_engine.models.job_queue import JobQueue
from workflow_engine.models.workflow_node import WorkflowNode
from workflow_engine.models.workflow import Workflow
from workflow_client.celery_ingest_consumer \
    import run_task, fail
from workflow_client.client_settings import settings_attr_dict


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc'
    }

# @pytest.fixture(scope='session')
# def celery_parameters():
#     return {
#         'task_cls': 'workflow_client.celery_ingest_consumer'
#     }


def get_timeout_eta(timeout_seconds):
    return now() + timedelta(seconds=timeout_seconds)

@pytest.fixture
def task_5():
    pending, _ = RunState.objects.update_or_create(name='PENDING')
    running, _ = RunState.objects.update_or_create(name='RUNNING')
    failed_ex, _ = RunState.objects.update_or_create(name='FAILED_EXECUTION')
    failed, _ = RunState.objects.update_or_create(name='FAILED')

    workflow, _ = Workflow.objects.update_or_create(
        id=1)
    job_queue, _ = JobQueue.objects.update_or_create(
        id=7,
        defaults={
            'job_strategy_class': 'workflow_engine.strategies.base_strategy.BaseStrategy'})
    workflow_node, _ = WorkflowNode.objects.update_or_create(
        id=1,
        defaults={
            'workflow': workflow,
            'job_queue': job_queue})
    job, _ = Job.objects.update_or_create(
        id=2,
        defaults = {
            'enqueued_object_id': 56,
            'run_state_id': pending.id,
            'workflow_node': workflow_node})
    task, _ = Task.objects.update_or_create(
        id=5,
        job=job,
        defaults={
            'full_executable': 'mock_task',
            'run_state_id': pending.id})

    return task

@pytest.mark.django_db
@pytest.mark.parametrize(
    'run_seconds,timeout_seconds,transition_success', [
    (10,2,False),
    (2,10,True)])
def xtest_run_task(celery_session_worker,
                  task_5,
                  run_seconds,
                  timeout_seconds,
                  transition_success):
    name = 'em_2d_montage'
    args = ('RUNNING', 5)

    def check_timeout(m, transition_expected):
        if transition_expected:
            m.assert_called()
        else:
            m.assert_not_called()

    do_run_mock = Mock(side_effect=lambda: sleep(run_seconds))
    do_transition_mock = Mock(name='transition mock')
    do_timeout_mock = Mock(name='timeout mock')
    do_timeout_mock.side_effect = [
        lambda: check_timeout(do_transition_mock, transition_success),
        lambda: check_timeout(do_transition_mock, transition_success)]
    get_task_mock = MagicMock(
        name='get_current_task_by_id',
        return_value=5)

    on_message_handler = Mock()
    mock_strategy = Mock(name='mock_strategy')

    with patch(
        'workflow_client.celery_ingest_consumer.do_running',
        do_run_mock):
        with patch(
            'workflow_client.celery_ingest_consumer.do_transition',
            do_transition_mock):
            with patch(
                'workflow_client.celery_ingest_consumer.do_timeout',
                do_timeout_mock):
                result = run_task.apply_async(
                    (name, args),
                    link=enqueue_next.s(),
                    link_error=fail.s())
                timeout_result = timeout.apply_async(
                    (762,),
                    eta=get_timeout_eta(timeout_seconds))

                outpt = result.get(
                    on_message=on_message_handler,
                    propagate=False)
                timeout_outp = timeout_result.get()

    #assert outpt == 'mock return'

    assert not result.failed()
    assert result.state == 'SUCCESS'
    do_run_mock.assert_called()
    #assert len(on_message_handler.call_args_list) == 3
    do_timeout_mock.assert_called()
    do_transition_mock.assert_called()
