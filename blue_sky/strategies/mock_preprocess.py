from .mock_execution_strategy import MockExecutionStrategy
from blue_sky.models import Observation
from django_fsm import can_proceed
import logging
import copy

class MockPreprocess(MockExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_preprocess')

    _base_input_dict = {
        'arg1': 5,
        'arg2': 'overwrite me',
        'nested': {
            'nested_arg': 'yay'
        }
    }

    def can_transition(self, enqueued_object, from_node):
        del from_node

        return enqueued_object.__class__ == Observation

    def check_input_state(self, observation_object):
        if can_proceed(observation_object.start_processing):
            observation_object.start_processing()
            observation_object.save()
        else:
            msg = '{} must be in {} state'.format(
                observation_object,
                observation_object.__class__.STATE.OBSERVATION_PENDING
            )
            MockPreprocess._log.error(msg)
            raise Exception(msg)

    def get_input(self, enqueued_object, storage_directory, task):
        observation_object = enqueued_object
        del storage_directory  # unused arg
        del task  # unused arg

        self.check_input_state(observation_object)
        inp = copy.deepcopy(MockPreprocess._base_input_dict)
    
        inp['arg1'] = 7  # settings.ARG_1

        return inp

    def get_or_create_task_storage_directory(self, task):
        return '.'
