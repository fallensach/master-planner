from django.db import models
    
class Course(models.Model):
    course_code = models.CharField(max_length=6, primary_key=True)
    examinator = models.CharField(max_length=50)
    course_name = models.CharField(max_length=120)
    level = models.CharField(max_length=20)
    vof = models.CharField(max_length=5)
    campus = models.CharField(max_length=20)

class Schedule(models.Model):
    schedule_id = models.IntegerField(primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    period = models.IntegerField()
    semester = models.CharField(max_length=2)
    block = models.IntegerField()
    
class MainField(models.Model):
    field_name = models.CharField(max_length=15, primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)

class Profile(models.Model):
    profile_name = models.CharField(max_length=50, primary_key=True)
    profile_courses = models.ManyToManyField(Course)
    
class Program(models.Model):
    program_code = models.CharField(max_length=10, primary_key=True)
    program_profiles = models.ManyToManyField(Profile)