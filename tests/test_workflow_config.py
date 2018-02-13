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
import os
import logging
from workflow_engine.workflow_config import WorkflowConfig
from django.db import transaction
from workflow_engine.models.executable import Executable
from workflow_engine.models.job_queue import JobQueue
from workflow_engine.models.workflow import Workflow
from workflow_engine.models.workflow_node import WorkflowNode
from workflow_engine.models.run_state import RunState
try:
    import __builtin__ as builtins  # @UnresolvedImport
except:
    import builtins  # @UnresolvedImport

_log = logging.getLogger('test_output')


_TEST_CONFIG_YAML_ONE_NODE = """
executables:
    mock:
        name: 'Mock Executable'
        path: '/data/aibstemp/timf/example_data/bin/mock_executable'
        pbs_queue: 'lims2'
        pbs_processor: 'vmem=128g'
        pbs_walltime: 'walltime=5:00:00'
run_states:
    - "PENDING"
    - "QUEUED"
    - "RUNNING"
    - "FINISHED_EXECUTION"
    - "FAILED_EXECUTION"
    - "FAILED"
    - "SUCCESS"
    - "PROCESS_KILLED"
workflows:
    test_workflow:
        ingest: "blue_sky.strategies.mock_ingest.MockIngest"

        states:
            - key: "start"
              label: "Start"
              class: "blue_sky.strategies.mock_analyze.MockAnalyze"
              enqueued_class: "development.models.e_o.EO"
              executable: "mock"
        graph:
            - [ "start", [ ] ]
"""

_TEST_CONFIG_YAML_TWO_NODES = """
executables:
    mock:
        name: 'Mock Executable'
        path: '/data/aibstemp/timf/example_data/bin/mock_executable'
        pbs_queue: 'lims2'
        pbs_processor: 'vmem=128g'
        pbs_walltime: 'walltime=5:00:00'
run_states:
    - "PENDING"
    - "QUEUED"
    - "RUNNING"
    - "FINISHED_EXECUTION"
    - "FAILED_EXECUTION"
    - "FAILED"
    - "SUCCESS"
    - "PROCESS_KILLED"
workflows:
    test_workflow:
        ingest: "development.strategies.lens_correction_ingest.LensCorrectionIngest"

        states:
            - key: "start"
              label: "Start"
              class: "development.strategies.start.Start"
              enqueued_class: "development.models.e_o.EO"
              executable: "mock"
            - key: "continue"
              label: "Continue"
              class: "development.strategies.continue.Continue"
              enqueued_class: "development.models.e_o.EO"
              executable: "mock"
        graph:
            - [ "start", [ "continue" ] ]
"""

@pytest.fixture
def workflow_config():
    return WorkflowConfig


def test_workflow_config(workflow_config):
    assert workflow_config is not None

# @transaction.atomic
@pytest.mark.django_db
@pytest.mark.parametrize(
    "yaml_text", [
        (_TEST_CONFIG_YAML_ONE_NODE),
        (_TEST_CONFIG_YAML_TWO_NODES)
    ])
def test_create_workflow(workflow_config,
                         yaml_text):
    with patch(builtins.__name__ + ".open",
        mock_open(read_data=yaml_text)):
        WorkflowConfig.create_workflow(
            os.path.join(os.path.dirname(__file__), 'dev.yml'))

    for e in Executable.objects.all():
        _log.info(e.name)
        jq = e.get_job_queues()
        _log.info("Job queue: " + str(len(jq)))

    for q in JobQueue.objects.all():
        _log.info("Q: %s" % (q.name))

    workflow_nodes = \
        WorkflowNode.objects.filter(
            workflow=Workflow.objects.get(name='test_workflow'),
            parent=None)

    for n in workflow_nodes:
        _log.info("N: %s->%s" % (str(n), str(n.parent)))
    assert len(workflow_nodes) == 1
    # eq = JobQueue.objects.get(
    #     name='lens_correction generate_lens_correction_transform')
    # eq.
    
    for rs in RunState.objects.all():
        _log.info("Run States %s" % (rs.name))

    # Workflow.start_workflow('em_2d_montage',
    #                         enqueued_object)


@pytest.mark.parametrize(
    "yaml_text", [
        (_TEST_CONFIG_YAML_ONE_NODE),
        (_TEST_CONFIG_YAML_TWO_NODES)
    ])
def test_from_yaml_file(workflow_config,
                        yaml_text):
    with patch(builtins.__name__ + ".open",
        mock_open(read_data=yaml_text)):
        wc = workflow_config.from_yaml_file(
            os.path.join(os.path.dirname(__file__),
                         'dev.yml'))

    for w in wc['flows']:
        print("\nworkflow: " + w.name)
        for k in w.states.keys():
            s = w.states[k]
            line = [k, ' ', s['label']]
            if s['class'] is not None:
                line.extend([' (', s['class'], ')'])
            if s['manual']:
                line.append(' (m)')
            if s['workflow']:
                line.append(' (w)')
            print(''.join(line))


@pytest.mark.django_db
def test_delete_all_workflows():
    WorkflowConfig.delete_all_workflows()