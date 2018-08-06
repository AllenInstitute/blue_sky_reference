from workflow_engine.strategies.execution_strategy import ExecutionStrategy
# from django.conf import settings
import logging
from workflow_engine.models.configuration import Configuration
import copy

class MockParametrizedAnalyze(ExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_analyze')

    def get_input(self, enqueued_object, storage_directory, task):
        strategy_configuration = \
            Configuration.objects.filter(
                attachable_id=1)
        inp = copy.deepcopy(strategy_configuration.json_object)
    
        inp['arg1'] = 7  # settings.ARG_1

        return inp 

    def on_finishing(self, em_mset, results, task):
        self.check_key(results, 'arg2')
