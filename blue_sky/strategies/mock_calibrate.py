from workflow_engine.strategies.execution_strategy import ExecutionStrategy
from blue_sky.models.calibration import Calibration
import logging
import copy

class MockCalibrate(ExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_calibrate')

    _base_input_dict = {
        'arg1': 5,
        'arg2': 'overwrite me',
        'nested': {
            'nested_arg': 'yay'
        }
    }

    def can_transition(self, calibration, from_node):
        return calibration.__class__ == Calibration

    def get_input(self, enqueued_object, storage_directory, task):
        inp = copy.deepcopy(MockCalibrate._base_input_dict)
    
        inp['arg1'] = 7  # settings.ARG_1

        return inp 

    def on_finishing(self, calibration_object, results, task):
        # self.check_key(results, 'arg2')
        # observation.start_processing()
        # observation.save()
        pass
