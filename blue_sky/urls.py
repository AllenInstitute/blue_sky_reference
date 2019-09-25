"""blue_sky URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path
from workflow_engine.views import home_view
from .views.demo_job_grid_view import demo_job_grid


app_name = 'blue_sky'

urlpatterns = [
    re_path(r'^workflow_engine/', include('workflow_engine.urls')),

    re_path(r'^$', home_view.index, name='index'),

    re_path(
        r'^at_em/faster_job_grid$',
        demo_job_grid,
        name='job_grid'
    ),

]
