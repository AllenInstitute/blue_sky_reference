from workflow_engine.strategies.execution_strategy import ExecutionStrategy
from blue_sky.models.observation_group import ObservationGroup
from blue_sky.models.group_assignment import GroupAssignment
from django_fsm import can_proceed
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
                'object_state': ObservationGroup.STATE.GROUP_INCOMPLETE
            })

        group_assign, _ = GroupAssignment.objects.get_or_create(
            observation=observation,
            group=group)

        return [ observation ]

    def get_input(self, observation, storage_directory, task):
        inp = copy.deepcopy(MockGroupAssignment._base_input_dict)

        inp['arg1'] = str(observation)

        return inp 

    def set_output_state(self, observation_object):
        if can_proceed(observation_object.group):
            observation_object.group()
            observation_object.save()
        else:
            if (observation_object.object_state ==
                observation_object.__class__.STATE.OBSERVATION_GROUPED):
                MockGroupAssignment._log.warn(
                    '{} is already in state {}'.format(
                        observation_object,
                        observation_object.__class__.STATE.OBSERVATION_GROUPED
                    )
                )

    def on_finishing(self, observation_object, results, task):
        self.set_output_state(observation_object)
        observation_object.save()
