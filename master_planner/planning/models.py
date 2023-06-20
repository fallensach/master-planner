from django.db import models
from scrappy.program_plan import ProgramPlan
    
class Course(models.Model):
    course_code = models.CharField(max_length=6, primary_key=True)
    examinator = models.CharField(max_length=50, null=True, blank=True)
    course_name = models.CharField(max_length=120)
    level = models.CharField(max_length=20)
    vof = models.CharField(max_length=5)
    campus = models.CharField(max_length=20, blank=True, null=True)

class Schedule(models.Model):
    schedule_id = models.IntegerField(primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    period = models.IntegerField()
    semester = models.CharField(max_length=10)
    block = models.IntegerField()
    
class MainField(models.Model):
    field_name = models.CharField(max_length=15, primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)

class Profile(models.Model):
    profile_name = models.CharField(max_length=50, primary_key=True)
    profile_code = models.CharField(max_length=10)
    profile_courses = models.ManyToManyField(Course)
    
class Program(models.Model):
    program_code = models.CharField(max_length=10, primary_key=True)
    program_profiles = models.ManyToManyField(Profile)
    program_courses = models.ManyToManyField(Course)
    
def register_program(program_code: str):
    program_exists = Program.objects.filter(program_code=program_code.upper()).exists()
    if not program_exists:
        program = ProgramPlan(program_code.upper())
        courses = register_courses(program)
        register_profiles(program)
        add_courses(program, courses)

def register_courses(program: ProgramPlan) -> list[Course]:
    general_courses = program.courses()
    courses = []
    
    for course in general_courses:
        new_course = Course(
                    course_code = course["course_code"], 
                    course_name = course["course_name"],
                    level = course["level"],
                    vof = course["vof"],
                )
        courses.append(new_course)
        new_course.save()
        
    return courses

def register_profiles(program: ProgramPlan):
    profiles = program.profiles()
    
    for name, code in profiles.items():
        profile_courses = program.courses(code)
        courses = []
        for course in profile_courses:
            profile_course = Course(
                course_code = course["course_code"], 
                course_name = course["course_name"],
                level = course["level"],
                vof = course["vof"],
            )
            profile_course.save()
            courses.append(profile_course)
            
        profile = Profile(name, code)
        new_program = Program(program.program_code)
        new_program.save()
        profile.save()
        profile.profile_courses.add(*courses)
        profile.save()
        new_program.program_profiles.add(profile)
        new_program.save()

def add_courses(program: ProgramPlan, courses: list[Course]):
    program_add = Program.objects.get(program_code=program.program_code.upper())
    program_add.program_courses.add(*courses)
    program_add.save()
        
        
        
    
    
    