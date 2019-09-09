from .mock_execution_strategy import MockExecutionStrategy
from blue_sky.models import Calibration, Observation
from django_fsm import can_proceed
import logging
import copy

class MockAnalyze(MockExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_analyze')

    _base_input_dict = {
        'arg1': 5,
        'arg2': 'overwrite me',
        'nested': {
            'nested_arg': 'yay'
        }
    }

    def must_wait(self, enqueued_object):
        if (enqueued_object.__class__ is Calibration or
            enqueued_object.__class__ is Observation and
            (enqueued_object.calibration is not None) and
            (enqueued_object.calibration.object_state ==
             Calibration.STATE.CALIBRATION_DONE)):
            return True
        else:
            return False

    def transform_objects_for_queue(self, enqueued_object):
        if enqueued_object.__class__ is Calibration:
            return list(
                enqueued_object.observation_set.filter(
                    object_state=Observation.STATE.OBSERVATION_PENDING
                )
            )
        elif enqueued_object.__class__ is Observation:
            return [enqueued_object]
        else:
            MockAnalyze._log.warning(
                "Unexpected enqueued object %s",
                str(enqueued_object)
            )
            return []

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
        #self.check_key(results, 'arg2')

        if can_proceed(observation.stop_processing):
            observation.stop_processing()
            observation.save()
        else:
            if (observation.object_state ==
                observation.__class__.STATE.OBSERVATION_QC):
                MockAnalyze._log.warning(
                    '%s is already in state %s',
                    str(observation),
                    observation.__class__.STATE.OBSERVATION_QC
                )
