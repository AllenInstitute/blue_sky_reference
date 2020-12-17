from .mock_execution_strategy import MockExecutionStrategy
from blue_sky.models.observation_group import ObservationGroup
from blue_sky.models.group_assignment import GroupAssignment
from django_fsm import can_proceed
import logging
import copy


class MockGroupAssignment(MockExecutionStrategy):
    _log = logging.getLogger('blue_sky.mock_group_assignment')

    _base_input_dict = {}

    def transform_objects_for_queue(self, observation):
        group_index = int(observation.arg1) // ObservationGroup.GROUP_SIZE

        group_label = 'Group {}'.format(group_index)

        group, _ = ObservationGroup.objects.get_or_create(
            label=group_label,
            defaults={
                'object_state': ObservationGroup.STATE.GROUP_INCOMPLETE
            })

        GroupAssignment.objects.get_or_create(
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
                MockGroupAssignment._log.warning(
                    '%s is already in state %s',
                    str(observation_object),
                    observation_object.__class__.STATE.OBSERVATION_GROUPED
                )

    def on_finishing(self, observation_object, results, task):
        self.set_output_state(observation_object)
        observation_object.save()
