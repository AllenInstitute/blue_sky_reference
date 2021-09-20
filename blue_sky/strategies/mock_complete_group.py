from .mock_execution_strategy import MockExecutionStrategy
from blue_sky.models import Observation, ObservationGroup
import logging
import copy

class MockCompleteGroup(MockExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_complete_group')

    _base_input_dict = {}

    def transform_objects_for_queue(self, observation):
        objects = set()

        groups = observation.groups.all()

        for grp in groups:
            observations = grp.observations.filter(
                object_state=Observation.STATE.OBSERVATION_DONE
            )

            if observations.count() == ObservationGroup.GROUP_SIZE:
                objects = objects | { grp }

        return list(objects)

    def get_input(self, group, storage_directory, task):
        inp = copy.deepcopy(MockCompleteGroup._base_input_dict)

        inp['arg1'] = str(group)

        return inp 

    def on_finishing(self, group, results, task):
        group.complete()
        group.save()
