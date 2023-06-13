from django.db import models

class Course(models.Model):
    course_code = models.CharField(max_length=6, primary_key=True)
    examinator = models.CharField(max_length=50)
    level = models.CharField(max_length=20)
    vof = models.CharField(max_length=5)
    campus = models.CharField(max_length=20)