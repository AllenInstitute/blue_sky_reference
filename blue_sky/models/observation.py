from django.db import models
from workflow_engine.mixins import Enqueueable, Stateful
from django_fsm import transition


class Observation(Enqueueable, Stateful, models.Model):
    '''Represents experimental data

    .. figure:: _static/observation_states.png
        :height: 300px
    '''

    class STATE:
        OBSERVATION_PENDING = "PENDING"
        OBSERVATION_PROCESSING = "PROCESSING"
        OBSERVATION_QC = "QC"
        OBSERVATION_QC_FAILED = "QC_FAILED"
        OBSERVATION_QC_PASSED = "QC_PASSED"
        OBSERVATION_GROUPED = "GROUPED"
        OBSERVATION_DONE = "DONE"

    arg1 = models.IntegerField(null=True)
    arg2 = models.CharField(max_length=255, null=True)
    arg3 = models.CharField(max_length=255, null=True)
    groups = models.ManyToManyField(
        'ObservationGroup', related_name='observations',
        through='GroupAssignment')
    calibration = models.ForeignKey(
        'Calibration',
        null=True, blank=True)


    def __str__(self):
        return str(self.arg2)

    @transition(
        field='object_state',
        source=[
            STATE.OBSERVATION_PENDING,
            STATE.OBSERVATION_PROCESSING
        ],
        target=STATE.OBSERVATION_PROCESSING)
    def start_processing(self):
        pass

    @transition(
        field='object_state',
        source=[
            STATE.OBSERVATION_PROCESSING,
            STATE.OBSERVATION_QC
        ],
        target=STATE.OBSERVATION_QC)
    def stop_processing(self):
        pass

    @transition(
        field='object_state',
        source=[
            STATE.OBSERVATION_QC,
            STATE.OBSERVATION_QC_FAILED
        ],
        target=STATE.OBSERVATION_QC_FAILED)
    def fail_qc(self):
        pass

    @transition(
        field='object_state',
        source=[
            STATE.OBSERVATION_QC,
            STATE.OBSERVATION_QC_PASSED
        ],
        target=STATE.OBSERVATION_QC_PASSED)
    def pass_qc(self):
        pass

    @transition(
        field='object_state',
        source=[
            STATE.OBSERVATION_QC_PASSED,
            STATE.OBSERVATION_GROUPED
        ],
        target=STATE.OBSERVATION_GROUPED)
    def group(self):
        pass

    @transition(
        field='object_state',
        source=[
            STATE.OBSERVATION_GROUPED,
            STATE.OBSERVATION_DONE
        ],
        target=STATE.OBSERVATION_DONE)
    def done(self):
        pass
