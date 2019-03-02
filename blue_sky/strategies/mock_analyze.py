from workflow_engine.strategies.execution_strategy import ExecutionStrategy
from django_fsm import can_proceed
import logging
import copy

class MockAnalyze(ExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_analyze')

    _base_input_dict = {
        'arg1': 5,
        'arg2': 'overwrite me',
        'nested': {
            'nested_arg': 'yay'
        }
    }

    def get_input(self, observation, storage_directory, task):
        if not can_proceed(observation.stop_processing):
            msg = '{} must be in {} state'.format(
                observation,
                observation.__class__.STATE.OBSERVATION_PROCESSING
            )
            MockAnalyze._log.error(msg)
            raise Exception(msg)

        inp = copy.deepcopy(MockAnalyze._base_input_dict)
    
        inp['arg1'] = 7  # settings.ARG_1

        return inp 

    def on_finishing(self, observation, results, task):
        self.check_key(results, 'arg2')

        if can_proceed(observation.stop_processing):
            observation.stop_processing()
            observation.save()
        else:
            if (observation.object_state ==
                observation.__class__.STATE.OBSERVATION_QC):
                MockAnalyze._log.warn('{} is already in state {}'.format(
                    observation,
                    observation.__class__.STATE.OBSERVATION_QC
                ))
