from django.db import models


class GroupAssignment(models.Model):
    observation = models.ForeignKey('Observation')
    group = models.ForeignKey('ObservationGroup')

    def __str__(self):
        return "{} in {}".format(self.observation, self.group)