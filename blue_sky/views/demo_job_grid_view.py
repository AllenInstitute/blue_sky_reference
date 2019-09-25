from django.http import JsonResponse
from blue_sky.demo_job_grid import DemoJobGrid

def demo_job_grid(request):
    z_min = int(request.GET.get('z_min', None))
    z_max = int(request.GET.get('z_max', None))
    djg = DemoJobGrid(
        (z_min, z_max),
    )
    return JsonResponse(djg.get_dict())