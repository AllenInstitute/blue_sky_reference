# Allen Institute Software License - This software license is the 2-clause BSD
# license plus a third clause that prohibits redistribution for commercial
# purposes without further permission.
#
# Copyright 2017-2018. Allen Institute. All rights reserved.
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
from workflow_engine.strategies.ingest_strategy import IngestStrategy
from blue_sky.models import Calibration, Observation
import logging

class MockIngest(IngestStrategy):
    _log = logging.getLogger('blue_sky.strategies.mock_ingest')

    def get_workflow_name(self):
        return 'mock_workflow'

    def create_enqueued_object(self, message, tags=None):
        if tags is None or len(tags) == 0:
            tags = ['observation']

        if 'observation' in tags:
            # Reuses an existing object if arg1 is the same
            obs, _ = Observation.objects.update_or_create(
                arg1 = message['arg1'],
                defaults={
                    'arg2': message['arg2'],
                    'arg3': message['arg3'],
                    'calibration_id': (
                        message['calibration_id']
                        if 'calibration_id' in message
                        else None
                    ), 
                    'object_state': Observation.STATE.OBSERVATION_PENDING
                }
            )

            return obs, None

        elif 'calibration' in tags:
            cal = Calibration.objects.create(
                object_state=Calibration.STATE.CALIBRATION_PENDING,
                offset=message['offset']
            )

            return cal, None
        else:
            raise Exception('tags not recognized {}'.format(tags))


    def generate_response(self, ingested_obj):
        if ingested_obj.__class__ is Observation:
            return {
                'observation_id': ingested_obj.id
            }

        if ingested_obj.__class__ is Calibration:
            return {
                'calibration_id': ingested_obj.id
            }
