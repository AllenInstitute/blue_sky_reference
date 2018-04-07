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
from blue_sky.models.observation import Observation
from workflow_client.client_settings import settings_attr_dict
from workflow_engine.blue_sky_state_machine \
    import BlueSkyStateMachine
from workflow_engine.state_machine_yaml import StateMachineYaml


_test_transitions = settings_attr_dict({
    'PENDING': 'pending',
    'PROCESSING': 'processing',
    'DONE': 'done',
    'FAILED': 'failed'
})


@pytest.fixture
def state_yaml():
    return """
observation:
    states:
        - "pending"
        - "processing"
        - "qc"
        - "redo"
        - "qc_failed"
        - "qc_passed"
        - "failed"
        - "gap"
    transitions:
        - "-oxxxxox"
        - "x-oxxxxx"
        - "xo-ooooo"
        - "xxo-xxoo"
        - "xxoo-ooo"
        - "xxoxx-xx"
        - "xxoxxx-o"
        - "xxoxxxo-"
"""


@pytest.fixture
def observation_states(state_yaml):
    with patch("builtins.open",
        mock_open(read_data=state_yaml)):
        transitions = StateMachineYaml.from_yaml_file(
            'states.yml')

    return transitions


@pytest.fixture
def state_machine(observation_states):
    return BlueSkyStateMachine(observation_states)


def test_state_machine(state_machine):
    assert state_machine is not None


def test_machine_key(state_machine):
    assert state_machine.machine_key(
        Observation) == 'observation'


@pytest.mark.django_db
def test_transition(state_machine):
    obs = Observation(
        proc_state=state_machine.states(Observation).pending)
    obs.save()

    state_machine.transition(
        obs,
        'proc_state',
        _test_transitions.PROCESSING)


@pytest.mark.django_db
def test_illegal_transition(state_machine):
    obs = Observation(
        proc_state=state_machine.states(Observation).processing)
    obs.save()

    with pytest.raises(Exception):
        state_machine.transition(
            obs,
            'proc_state',
            state_machine.states.pending)


@pytest.mark.django_db
def test_no_transitions(state_machine):
    obs = Observation(
        proc_state=state_machine.states(Observation).processing)
    obs.save()

    with pytest.raises(Exception):
        state_machine.transition(
            obs,
            'proc_state',
            state_machine.states(Observation).pending)


@pytest.mark.django_db
def test_no_state_field(state_machine):
    obs = Observation(
        proc_state=_test_transitions.PENDING)
    obs.save()

    with pytest.raises(Exception):
        state_machine.transition(
            obs,
            'bad_state_field',
            state_machine.states(Observation).processing)


def test_from_yaml(state_yaml):
    with patch("builtins.open",
        mock_open(read_data=state_yaml)):
        l = StateMachineYaml.from_yaml_file(
            'states.yml')

        assert set(l.keys()) == { 'observation' }

