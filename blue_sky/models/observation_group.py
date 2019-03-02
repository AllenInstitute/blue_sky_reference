from django.db import models
from django_fsm import FSMField, transition

class ObservationGroup(models.Model):
    class STATE:
        GROUP_INCOMPLETE = "INCOMPLETE"
        GROUP_COMPLETE = "COMPLETE"

    label = models.CharField(max_length=255, null=True)
    object_state = FSMField(default=STATE.GROUP_INCOMPLETE)

    def __str__(self):
        return str(self.label)

    @transition(
        field='object_state',
        source=[
            STATE.GROUP_INCOMPLETE,
            STATE.GROUP_COMPLETE
        ],
        target=STATE.GROUP_COMPLETE)
    def complete(self):
        pass

