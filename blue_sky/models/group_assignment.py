from django.db import models
from workflow_engine.mixins import Enqueueable

class GroupAssignment(Enqueueable, models.Model):
    observation = models.ForeignKey(
        'Observation',
        on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        'ObservationGroup',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} in {}".format(self.observation, self.group)