from workflow_engine.strategies.execution_strategy import ExecutionStrategy
# from django.conf import settings
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

    def get_input(self, enqueued_object, storage_directory, task):
        inp = copy.deepcopy(MockAnalyze._base_input_dict)
    
        inp['arg1'] = 7  # settings.ARG_1

        return inp 

    def on_finishing(self, em_mset, results, task):
        self.check_key(results, 'arg2')
