from django.shortcuts import render
from blue_sky.models.observation import Observation
from django.http import HttpResponse
from django.template import loader
import django

context = {}


# Create your views here.