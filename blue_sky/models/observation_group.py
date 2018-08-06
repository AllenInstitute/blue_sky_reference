from django.db import models

class ObservationGroup(models.Model):
    label = models.CharField(max_length=255, null=True)
    group_state = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.label)
