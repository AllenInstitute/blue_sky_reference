from django.db import models
from django_fsm import transition
from workflow_engine.mixins import Enqueueable, Stateful

class ObservationGroup(Enqueueable, Stateful, models.Model):
    '''A collenction of experimental data to be processed together

    .. figure:: _static/observation_group_states.png
        :height: 300px
    '''

    class STATE:
        GROUP_INCOMPLETE = "INCOMPLETE"
        GROUP_COMPLETE = "COMPLETE"

    label = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.label)

    def reset_pending(self):
        self.object_state = ObservationGroup.STATE.GROUP_INCOMPLETE

    @transition(
        field='object_state',
        source=[
            STATE.GROUP_INCOMPLETE,
            STATE.GROUP_COMPLETE
        ],
        target=STATE.GROUP_COMPLETE)
    def complete(self):
        pass

