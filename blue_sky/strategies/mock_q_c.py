from workflow_engine.strategies.execution_strategy import ExecutionStrategy
from django_fsm import can_proceed
import logging
import copy

class MockQC(ExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_q_c')

    _base_input_dict = {
        'arg1': 5,
        'arg2': 'overwrite me',
        'nested': {
            'nested_arg': 'yay'
        }
    }

    def check_input_state(self, observation_object):
        if not can_proceed(observation_object.pass_qc):
            msg = '{} must be in {} state'.format(
                observation_object,
                observation_object.__class__.STATE.OBSERVATION_QC
            )
            MockQC._log.error(msg)
            raise Exception(msg)

    def get_input(self, observation_object, storage_directory, task):
        self.check_input_state(observation_object)
        inp = copy.deepcopy(MockQC._base_input_dict)
    
        inp['arg1'] = 7  # settings.ARG_1

        return inp 

    def set_output_state(self, observation_object):
        if can_proceed(observation_object.pass_qc):
            observation_object.pass_qc()
            observation_object.save()
        else:
            if (observation_object.object_state ==
                observation_object.__class__.STATE.OBSERVATION_QC_PASSED):
                MockQC._log.warn('{} is already in state {}'.format(
                    observation_object,
                    observation_object.__class__.STATE.OBSERVATION_QC_PASSED
                ))


    def on_finishing(self, observation_object, results, task):
        #self.check_key(results, 'arg2')
        self.set_output_state(observation_object)