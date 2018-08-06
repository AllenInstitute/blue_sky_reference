from workflow_engine.strategies.execution_strategy import ExecutionStrategy
from blue_sky.models.observation_group import ObservationGroup
from blue_sky.models.group_assignment import GroupAssignment
# from django.conf import settings
import logging
import copy

class MockGroupAssignment(ExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_group_assignment')

    _base_input_dict = {}

    def get_objects_for_queue(self, job):
        observation = job.enqueued_object
        tens = int(observation.arg1) // 10

        group_label = 'Group {}'.format(tens)

        group, _ = ObservationGroup.objects.get_or_create(
            label=group_label,
            defaults={
                'group_state': 'PENDING'
            })

        group_assign, _ = GroupAssignment.objects.get_or_create(
            observation=observation,
            group=group)

        return [ observation ]


    def get_input(self, observation, storage_directory, task):
        inp = copy.deepcopy(MockGroupAssignment._base_input_dict)

        inp['arg1'] = str(observation)

        return inp 

    def on_finishing(self, observation, results, task):
        observation.proc_state = 'GROUPED'
        observation.save()
