from django.db import models
from django_fsm import FSMField, transition


class Observation(models.Model):
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
    object_state = FSMField(default=STATE.OBSERVATION_PENDING)
    groups = models.ManyToManyField(
        'ObservationGroup', related_name='observations',
        through='GroupAssignment')

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
