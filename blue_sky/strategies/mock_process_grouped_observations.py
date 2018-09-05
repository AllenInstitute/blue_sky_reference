from workflow_engine.strategies.execution_strategy import ExecutionStrategy
from blue_sky.models import Observation
import logging
import copy

class MockProcessGroupedObservations(ExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_group_assignment')

    _base_input_dict = {}

    def get_objects_for_queue(self, job):
        objects = set()

        observation = job.enqueued_object
        groups = observation.groups.all()

        for grp in groups:
            observations = grp.observations.filter(
                object_state=Observation.STATE.OBSERVATION_GROUPED)

            if observations.count() == 10:
                objects = objects | set(observations)

        return list(objects) 

    def get_input(self, observation, storage_directory, task):
        inp = copy.deepcopy(MockProcessGroupedObservations._base_input_dict)

        inp['arg1'] = str(observation)

        return inp 

    def on_finishing(self, observation, results, task):
        observation.done()
        observation.save()
