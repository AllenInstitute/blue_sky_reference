from django.db import models
from workflow_engine.mixins import Enqueueable

class GroupAssignment(Enqueueable, models.Model):
    observation = models.ForeignKey('Observation')
    group = models.ForeignKey('ObservationGroup')

    def __str__(self):
        return "{} in {}".format(self.observation, self.group)