from workflow_engine.strategies.execution_strategy import ExecutionStrategy
from blue_sky.models import Observation
import logging
import copy

class MockCompleteGroup(ExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_complete_group')

    _base_input_dict = {}

    def get_objects_for_queue(self, job):
        objects = set()

        observation = job.enqueued_object
        groups = observation.groups.all()

        for grp in groups:
            observations = grp.observations.filter(
                object_state=Observation.STATE.OBSERVATION_DONE
            )

            if observations.count() == 10:
                objects = objects | { grp }

        return list(objects)

    def get_input(self, group, storage_directory, task):
        inp = copy.deepcopy(MockCompleteGroup._base_input_dict)

        inp['arg1'] = str(group)

        return inp 

    def on_finishing(self, group, results, task):
        group.complete()
        group.save()
