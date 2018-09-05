from django.contrib import admin
from blue_sky.models import Observation, ObservationGroup


class ObservationGroupInline(admin.StackedInline):
    model = Observation.groups.through
    extra=0

def reset_pending(modeladmin, request, queryset):
    for obs in queryset:
        obs.object_state = Observation.STATE.OBSERVATION_PENDING
        obs.save()

        for grp in obs.groups.all():
            grp.object_state = ObservationGroup.STATE.GROUP_INCOMPLETE
            grp.save()

class ObservationAdmin(admin.ModelAdmin):
    # change_list_template = 'admin/_change_list.html'
    list_display = [
        'id',
        'arg1',
        'arg2',
        'arg3',
        'object_state'
        ]
    list_select_related = []
    list_filter = ['object_state']
    actions = [reset_pending,]
    inlines = [ObservationGroupInline,]
