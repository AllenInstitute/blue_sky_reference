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
from tests.workflow_configurations \
    import TEST_CONFIG_YAML_TWO_NODES
from workflow_engine.provenance import Provenance
import simplejson as json


try:
    import __builtin__ as builtins  # @UnresolvedImport
except:
    import builtins  # @UnresolvedImport

_log = logging.getLogger('test_provenance')

_EXAMPLE_FREEZE="""
pyparsing==2.2.0
PySocks==1.6.7
python-dateutil==2.6.1
pytz==2017.3
PyWavelets==0.5.2
PyYAML==3.12
render-python==1.1.0
requests==2.18.4
requests-toolbelt==0.8.0
ruamel-yaml==0.11.14
scikit-image==0.13.1
scipy==1.0.0
"""

_EXAMPLE_BLUE_SKY_SETTINGS = """
MESSAGE_QUEUE_HOST: example.org
MESSAGE_QUEUE_PORT: 9008
MESSAGE_QUEUE_USER: blue_sky_user
MESSAGE_QUEUE_PASSWORD: blue_sky_user
CELERY_MESSAGE_QUEUE_NAME: celery_at_em_imaging_workflow
DEFAULT_MESSAGE_QUEUE_NAME: null
WORKFLOW_CONFIG_YAML: ./workflow_config.yml
"""

@pytest.mark.skipif(True, reason='written')
def test_parse_freeze():
    with patch(builtins.__name__ + ".open",
        mock_open(read_data=_EXAMPLE_FREEZE),
        create=True) as mo:
        p = Provenance()
        p.read_pip_freeze_dependencies('freeze.txt')

    assert p.json_dict['pip'] is not None
    assert len(p.json_dict['pip']) == 12
    mo.assert_called_once()


@patch.dict(os.environ,
                 {'BLUE_SKY_SETTINGS': 'blue_sky_test_config.yml'})
def test_record_blue_sky_configuration():
    with patch(builtins.__name__ + ".open",
        mock_open(read_data=_EXAMPLE_BLUE_SKY_SETTINGS),
        create=True) as mo:
        p = Provenance()
        p.record_blue_sky_configuration('blue_sky_test_config.yml')

    assert p.json_dict['blue_sky'] is not None

    mo.assert_called_once_with('blue_sky_test_config.yml')
    assert 'example.org' == \
        p.json_dict['blue_sky']['MESSAGE_QUEUE_HOST']
    assert 9008 == \
        p.json_dict['blue_sky']['MESSAGE_QUEUE_PORT']
    assert 'blue_sky_user' == \
        p.json_dict['blue_sky']['MESSAGE_QUEUE_USER']
    assert 'celery_at_em_imaging_workflow' == \
        p.json_dict['blue_sky']['CELERY_MESSAGE_QUEUE_NAME']
    assert None == \
        p.json_dict['blue_sky']['DEFAULT_MESSAGE_QUEUE_NAME']
    assert './workflow_config.yml' == \
        p.json_dict['blue_sky']['WORKFLOW_CONFIG_YAML']


@pytest.mark.skipif(True, reason='written')
def test_record_django_settings():
    p = Provenance()
    keys = ['BASE_DIR', 'INSTALLED_APPS', 'MIDDLEWARE']
    p.record_django_settings(keys)

    assert p.json_dict['django'] is not None

    for k in keys:
        assert p.json_dict['django'][k] is not None


@pytest.mark.skipif(True, reason='unimplemented')
def test_record_executable_configuration():
    assert False


@pytest.mark.skipif(True, reason='written')
def test_record_workflow_configuration():
    with patch(builtins.__name__ + ".open",
        mock_open(read_data=TEST_CONFIG_YAML_TWO_NODES),
        create=True) as mo:
        p = Provenance()
        p.record_workflow_configuration('workflow.yml')

    assert p.json_dict['workflow'] is not None

    mo.assert_called_once_with('workflow.yml', 'r')
    assert 'executables' in p.json_dict['workflow']
    assert 'run_states' in p.json_dict['workflow']
    assert 'workflows' in p.json_dict['workflow']
