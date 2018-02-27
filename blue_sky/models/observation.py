from django.db import models

class Observation(models.Model):
    arg1 = models.IntegerField(null=True)
    arg2 = models.CharField(max_length=255, null=True)
    arg3 = models.CharField(max_length=255, null=True)
    proc_state = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.arg2)
