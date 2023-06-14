from django.contrib import admin
from .models import *

models = [Program, Profile, Course, Schedule, MainField]

admin.site.register(models)
