from django.contrib import admin
from blue_sky.models.observation import Observation


class ObservationGroupInline(admin.StackedInline):
    model = Observation.groups.through
    extra=0

def reset_pending(modeladmin, request, queryset):
    for obs in queryset:
        obs.proc_state = 'PENDING'
        obs.save()

        for grp in obs.groups.all():
            grp.group_state = 'PENDING'
            grp.save()

class ObservationAdmin(admin.ModelAdmin):
    # change_list_template = 'admin/_change_list.html'
    list_display = [
        'id',
        'arg1',
        'arg2',
        'arg3',
        'proc_state'
        ]
    list_select_related = []
    list_filter = ['proc_state']
    actions = [reset_pending,]
    inlines = [ObservationGroupInline,]
