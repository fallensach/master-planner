from django.contrib import admin
from .models import *

models = [Program, Profile, Course, Schedule, MainField, Scheduler, Examination, SchedulersProfiles]

admin.site.register(models)
