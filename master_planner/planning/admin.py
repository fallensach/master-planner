from django.contrib import admin
from .models import *

models = [Program, Profile, Course, Schedule, MainField, Scheduler, Examination]

admin.site.register(models)
