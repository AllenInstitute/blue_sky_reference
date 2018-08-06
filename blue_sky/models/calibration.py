from django.db import models

class Calibration(models.Model):
    offset = models.IntegerField(null=True)
    proc_state = models.CharField(max_length=255, null=True)


    def __str__(self):
        return str(self.offset)
