from django.db import models
from course import Course

class Schedule(models.Model):
    schedule_id = models.IntegerField(primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    period = models.IntegerField()
    semester = models.CharField(max_length=2)
    block = models.IntegerField()