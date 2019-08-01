from django.contrib import admin
from blue_sky.models import Calibration


class CalibrationAdmin(admin.ModelAdmin):
    # change_list_template = 'admin/_change_list.html'
    list_display = (
        'id',
        'offset',
        'object_state'
    )
    list_select_related = []
    list_filter = ('object_state',)
