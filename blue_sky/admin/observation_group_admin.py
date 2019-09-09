from django.contrib import admin
from blue_sky.models import ObservationGroup


def reset_incomplete(modeladmin, request, queryset):
    for grp in queryset:
        grp.object_state = ObservationGroup.STATE.GROUP_INCOMPLETE
        grp.save()

class ObservationGroupAdmin(admin.ModelAdmin):
    # change_list_template = 'admin/_change_list.html'
    list_display = [
        'id',
        'label',
        'object_state'
        ]
    list_select_related = []
    list_filter = ['object_state']
    actions = [reset_incomplete,]
    inlines = []
