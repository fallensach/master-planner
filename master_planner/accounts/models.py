from django.db import models
from django.contrib.auth.models import User
from planning.models import Program, Schedule

class Account(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    program_code = models.ForeignKey(Program, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Schedule, blank=True)
    