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
from workflow_engine.models.well_known_file import WellKnownFile
from blue_sky.models.observation import Observation
from mock import patch, Mock
from workflow_engine.models.task import Task
from tests.workflow.workflow_fixtures \
    import run_states, workflow_node_1, task_5, \
    running_task_5, mock_executable

@pytest.mark.django_db
def test_well_known_file(running_task_5):
    job = Mock()
    job.id = 1234
    obs = Observation(
        arg1=5, arg2='this', arg3='that', proc_state='WA')
    obs.save()

    full_path1 = '/this/is/a/test.txt'
    full_path2 = '/this/is/also/a/test.txt'
    wkf_type = 'cruft'

    with patch('os.path.exists',
               Mock(return_value=True)) as ope:
        WellKnownFile.set(
            full_path1, obs, wkf_type, running_task_5)
        ope.assert_called_with('/this/is/a/test.txt')
        WellKnownFile.set(
            full_path2, obs, wkf_type, running_task_5)
        ope.assert_called_with('/this/is/also/a/test.txt')

    wkf = WellKnownFile.get(obs, wkf_type)
    assert wkf == full_path2
    