from django.db import models
from django_fsm import transition
from workflow_engine.mixins import Enqueueable, Stateful

class Calibration(Enqueueable, Stateful, models.Model):
    '''Represents information needed to adjust a
    :class:`Observation<blue_sky.models.observation.Observation>`

    .. figure:: _static/calibration_states.png
        :height: 300px
    '''
    class STATE:
        CALIBRATION_PENDING = "PENDING"
        CALIBRATION_DONE = "DONE"

    offset = models.IntegerField(null=True)

    def __str__(self):
        return str(self.offset)

    @transition(
        field='object_state',
        source=[
            STATE.CALIBRATION_PENDING,
            STATE.CALIBRATION_DONE
        ],
        target=STATE.CALIBRATION_DONE)
    def done(self):
        pass
