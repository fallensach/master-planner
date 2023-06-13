from django.db import models

class Program(models.Model):
    program_code = models.CharField(max_length=10, primary_key=True)