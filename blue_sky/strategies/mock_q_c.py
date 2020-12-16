from .mock_execution_strategy import MockExecutionStrategy
from django_fsm import can_proceed
import logging
import copy

class MockQC(MockExecutionStrategy):
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

    def is_even(self, observation_object):
        return (observation_object.arg1 % 2 == 0)

    def set_output_state(self, observation_object):
        if self.is_even(observation_object):
            observation_object.fail_qc()
            observation_object.save()

        elif can_proceed(observation_object.pass_qc):
            observation_object.pass_qc()
            observation_object.save()

        else:
            if (observation_object.object_state ==
                observation_object.__class__.STATE.OBSERVATION_QC_PASSED):
                MockQC._log.warning(
                    '%s is already in state %s',
                    str(observation_object),
                    observation_object.__class__.STATE.OBSERVATION_QC_PASSED
                )


    def on_finishing(self, observation_object, results, task):
        self.set_output_state(observation_object)
