from django.contrib import admin
from blue_sky.models.observation import Observation
from blue_sky.admin.observation_admin import ObservationAdmin
from blue_sky.admin.calibration_admin import CalibrationAdmin
from blue_sky.admin.observation_group_admin import ObservationGroupAdmin
from blue_sky.models.calibration import Calibration
from blue_sky.models.observation_group import ObservationGroup
from blue_sky.models.group_assignment import GroupAssignment

# Register your models here.
admin.site.register(Observation, ObservationAdmin)
admin.site.register(Calibration, CalibrationAdmin)
admin.site.register(ObservationGroup, ObservationGroupAdmin)
admin.site.register(GroupAssignment)
