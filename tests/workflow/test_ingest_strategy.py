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
from tests.celery_helper import *
from mock import patch, mock_open, Mock, MagicMock
import os
from pkg_resources import resource_filename  # @UnresolvedImport


# @pytest.fixture(scope='session')
# def celery_parameters():
#     return {
#         'task_cls': 'workflow_client.celery_ingest_consumer'
#     }


def test_ingest_task(celery_session_worker):
    workflow = 'em_2d_montage'
    message = {'log_level': 'ERROR', 'acquisition_data': {
        'microscope_type': 'TEMCA', 'microscope': 'temca2', 'camera': {
            'width': 3840,
            'model': 'Ximea CB200MG',
            'camera_id': '44500428',
            'height': 3840
        },
            'acquisition_time': '2017-11-09T03:15:54+00:00',
            'overlap': 0.15
        },
        'metafile': '/allen/programs/celltypes/workgroups/em-connectomics/data/WorkFlow_test/000103/0/_metadata_20171108191554_15685_1R_0093_test_01_000103_0_.json',
        'reference_set_id': '9972961f-ce70-48d6-8ddd-461ccc84bcb6',
        'storage_directory': '/allen/programs/celltypes/workgroups/em-connectomics/data/WorkFlow_test/000103/0/',
        'section': {
            'specimen': '15685_1R',
            'z_index': 103,'sample_holder': '000103'
        }
    }
    tags = ['ReferenceSetTest']

    rv = MagicMock(
        return_value=settings_attr_dict({
            'WORKFLOW_CONFIG_YAML': 'test.yml'}))

    wc = settings_attr_dict({
        'FOO': "BAR"})

    ingest_strategies = {
        'em_2d_montage': 'development.strategies.in_strategy.InStrategy'
    }

    mock_ingest_strategy = Mock()
    mock_ingest_strategy.return_value.ingest_message = MagicMock(
        return_value = 'mock return')

    with patch(
        'workflow_client.celery_ingest_consumer.load_settings_yaml',
        rv) as load_settings_yaml_mock:
        with patch(
            'workflow_client.celery_ingest_consumer.load_ingest_strategy_names',
            Mock(return_value=ingest_strategies)):
            with patch(
                'workflow_client.celery_ingest_consumer.import_class',
                Mock(return_value=mock_ingest_strategy)):
                result = ingest_task.delay(workflow, message, tags)
                outpt = result.get()

    assert outpt == 'mock return'

    assert not result.failed()
    assert result.state == 'SUCCESS'
    load_settings_yaml_mock.assert_called_once()
