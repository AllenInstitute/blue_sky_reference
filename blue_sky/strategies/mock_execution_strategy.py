from workflow_engine.strategies.execution_strategy import ExecutionStrategy
import logging

class MockExecutionStrategy(ExecutionStrategy):
    _log = logging.getLogger('blue_sky.grategies.mock_execution_strategy')

    def get_input_file(self, task, create_dir=True):
        return None

    def get_output_file(self, task_obj):
        return None

    def on_finishing(self, observation_object, results, task):
        pass
