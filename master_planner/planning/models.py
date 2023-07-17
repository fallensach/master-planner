from django.db import models
from planning.management.commands.scrappy.program_plan import ProgramPlan
from typing import Union

    
class MainField(models.Model):
    field_name = models.CharField(max_length=15, primary_key=True)

    def __str__(self):
        return self.field_name

class Course(models.Model):
    course_code = models.CharField(max_length=6, primary_key=True)
    examinator = models.CharField(max_length=50, null=True)
    course_name = models.CharField(max_length=120)
    hp = models.CharField(max_length=5, default=1)
    level = models.CharField(max_length=20)
    vof = models.CharField(max_length=5)
    campus = models.CharField(max_length=20, null=True)
    main_fields = models.ManyToManyField(MainField)

    def __str__(self):
        return f"{self.course_code}, {self.hp}, {self.level}"

class Examination(models.Model):
    id = models.AutoField(primary_key=True)
    hp = models.CharField(max_length=5)
    name = models.CharField(max_length=50)
    grading = models.CharField(max_length=15)
    code = models.CharField(max_length=10)
    course = models.ForeignKey(Course,on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name, self.course

class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    period = models.IntegerField()
    semester = models.IntegerField()
    block = models.CharField(max_length=10)

    def __str__(self):
        return f"sem: {self.semester}, per: {self.period}, block: {self.block}"

class Profile(models.Model):
    profile_name = models.CharField(max_length=120)
    profile_code = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return self.profile_name

class Program(models.Model):
    program_code = models.CharField(max_length=10, primary_key=True)
    program_name = models.CharField(max_length=100)
    profiles = models.ManyToManyField(Profile)

    def __str__(self):
        return self.program_name

class Scheduler(models.Model):
    scheduler_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    profiles = models.ManyToManyField(Profile)
    linked = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{str(self.course)}\n{str(self.program)}\n{str(self.profiles)}\n{str(self.schedule)}"

def register_programs(program_data: list[tuple[str, str]]) -> list[Program]:
    
    new_programs = []
    for code, name in program_data:
        program, created = Program.objects.get_or_create(program_code=code, program_name=name)
        if created:
            new_programs.append(program)
    return new_programs

def register_profiles(program: Program, profile_data: list[tuple[str, str]]) -> None:
    for name, code in profile_data:
        profile, created = Profile.objects.get_or_create(profile_code=code,
                                                         defaults={"profile_name": name}
                                                         )
        program.profiles.add(profile)
        program.save()

def register_courses(program: Program, data: dict[Union[str, int]]) -> None:
    for course_data in data:
        course, created = Course.objects.get_or_create(course_code=course_data["course_code"],
                                                       defaults={"course_name": course_data["course_name"],
                                                                 "hp": course_data["hp"],
                                                                 "level": course_data["level"],
                                                                 "vof": course_data["vof"]
                                                        })
        schedule, created = Schedule.objects.get_or_create(block=course_data["block"],
                                                           semester=course_data["semester"],
                                                           period=course_data["period"]
                                                           )

        profile = Profile.objects.get(profile_code=course_data["profile_code"])
        # create instance of course in Scheduler
        scheduler, created = Scheduler.objects.get_or_create(course=course,
                                                             program=program, 
                                                             schedule=schedule,
                                                             )
        scheduler.profiles.add(profile)
        scheduler.save()

        if "*" in course.hp and schedule.period == 2:
            first_part = Scheduler.objects.get(course=course,
                                               program=program,
                                               profiles=profile,
                                               schedule__period=1,
                                               schedule__semester=schedule.semester
                                               )

            first_part.linked = scheduler
            scheduler.linked = first_part
            first_part.save()
            scheduler.save()

def get_courses_term(program: any, semester: str, profile=None): # TODO fix typing, döpa om funktion
    period_1 = list(Scheduler.objects.filter(program=program, 
                                             profiles=profile,
                                             schedule__semester=semester, 
                                             schedule__period=1))
    
    period_2 = list(Scheduler.objects.filter(program=program, 
                                             profiles=profile,
                                             schedule__semester=semester,
                                             schedule__period=2))

    return {1: period_1, 2: period_2}
