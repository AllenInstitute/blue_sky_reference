from .mock_execution_strategy import MockExecutionStrategy
from blue_sky.models import Observation, ObservationGroup
from django_fsm import can_proceed
import logging
import copy

class MockProcessGroupedObservations(MockExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_group_assignment')

    _base_input_dict = {}

    def transform_objects_for_queue(self, observation):
        objects = set()

        groups = observation.groups.all()

        for grp in groups:
            observations = grp.observations.filter(
                object_state=Observation.STATE.OBSERVATION_GROUPED)

            if observations.count() == ObservationGroup.GROUP_SIZE:
                objects = objects | set(observations)

        return list(objects) 

    def get_input(self, observation, storage_directory, task):
        inp = copy.deepcopy(MockProcessGroupedObservations._base_input_dict)

        inp['arg1'] = str(observation)

        return inp

    def on_finishing(self, observation, results, task):
        if can_proceed(observation.done):
            observation.done()
            observation.save()
        else:
            MockProcessGroupedObservations._log.warning(
                'cannot transition to done %s',
                str(observation)
            )
