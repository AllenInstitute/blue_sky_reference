from django.db import models
from django_fsm import FSMField, transition

class Calibration(models.Model):
    class STATE:
        CALIBRATION_PENDING = "PENDING"
        CALIBRATION_DONE = "DONE"

    offset = models.IntegerField(null=True)
    object_state = FSMField(default=STATE.CALIBRATION_PENDING)


    def __str__(self):
        return str(self.offset)

    @transition(
        field='object_state',
        source=STATE.CALIBRATION_PENDING,
        target=STATE.CALIBRATION_DONE)
    def done(self):
        pass
