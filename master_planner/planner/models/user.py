from django.db import models
from program import Program

class User(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    program_code = models.ForeignKey(Program, on_delete=models.CASCADE)