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
from workflow_engine.models.configuration import Configuration
from tests.workflow_configurations import TEST_CONFIG_YAML_TWO_NODES
from mock import patch, mock_open
import os
from workflow_engine.workflow_config import WorkflowConfig
from workflow_engine.models.workflow_node import WorkflowNode

@pytest.mark.django_db(transaction=True)
def test_configuration():
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
