from django.db import models, IntegrityError
from planning.management.commands.scrappy.program_plan import ProgramPlan
from typing import Union
import uuid

    
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
    campus = models.CharField(max_length=100, null=True)
    main_fields = models.ManyToManyField(MainField)

    def __str__(self):
        return f"Course: {self.course_code}"

class Examination(models.Model):
    id = models.AutoField(primary_key=True)
    hp = models.CharField(max_length=5)
    name = models.CharField(max_length=200)
    grading = models.CharField(max_length=15)
    code = models.CharField(max_length=10)
    course = models.ForeignKey(Course,on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Exam: {self.name}"

class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)    
    period = models.IntegerField()
    semester = models.IntegerField()
    block = models.CharField(max_length=10)

    def __str__(self):
        return f"Schedule: {self.semester}-{self.period}-{self.block}"

class Profile(models.Model):
    profile_name = models.CharField(max_length=120)
    profile_code = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return f"Profile: {self.profile_code}"

class Program(models.Model):
    program_code = models.CharField(max_length=10, primary_key=True)
    program_name = models.CharField(max_length=100)
    profiles = models.ManyToManyField(Profile)

    def __str__(self):
        return f"Program: {self.program_name}"

class Scheduler(models.Model):
    scheduler_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    profiles = models.ManyToManyField(Profile, through="SchedulersProfiles")
    linked = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Scheduler instance: {self.scheduler_id}"

class SchedulersProfiles(models.Model):
    scheduler = models.ForeignKey(Scheduler, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    vof = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.scheduler.scheduler_id}-{self.profile.profile_code}-{self.vof}"
    
def register_programs(program_data: list[tuple[str, str]]):
    programs = []
    for code, name in program_data:
        program = Program(program_code=code, program_name=name)
        programs.append(program)
    
    Program.objects.bulk_create(programs)

def register_profiles(profile_data: list[tuple[str, str, str]]) -> None:
    profiles = {}
    program_profile_list = []
    for name, code, program_code in profile_data:
        profile = Profile(profile_code=code,
                          profile_name=name
                          )
        program_profile = Program.profiles.through(program_id=program_code,
                                                   profile_id=code)
        program_profile_list.append(program_profile)
        profiles[code] = profile
    
    Profile.objects.bulk_create(profiles.values())
    Program.profiles.through.objects.bulk_create(program_profile_list)

def register_courses(data: dict[Union[str, int]]) -> None:
    # initialize containers for model objects
    schedulers = {}
    courses = set()
    schedules = {}
    scheduler_profiles_list = []
    
    # loop through course data
    for course_data in data:
        semester = course_data["semester"]
        period = course_data["period"]
        block = course_data["block"]
        program_id = course_data["program_code"]
        profile_id = course_data["profile_code"]
        course_id = course_data["course_code"]
        vof = course_data["vof"]
        
        course = Course(course_code=course_data["course_code"],
                        course_name=course_data["course_name"],
                        hp=course_data["hp"],
                        level=course_data["level"],
                        )
        courses.add(course)
        
        # create if nonexistent
        if (semester, period, block) in schedules:
            schedule = schedules[semester, period, block]
        else:
            schedule = Schedule(block=block,
                                semester=semester,
                                period=period
                                )
            schedules[semester, period, block] = schedule

        # create scheduler if nonexistent
        if (program_id, course_id, semester, period, block) in schedulers:
            scheduler_id = schedulers[program_id, course_id, semester, period, block].scheduler_id
        else:
            scheduler = Scheduler(course=course,
                                  program_id=program_id, 
                                  schedule=schedule,
                                  )

            # save the new scheduler objects to the dictionary so its id can be used later
            schedulers[program_id, course_id, semester, period, block] = scheduler
            scheduler_id = scheduler.scheduler_id
        

        # create a row in the many-to-many table and append it to the list for bulk_create
        scheduler_profile = SchedulersProfiles(profile_id=profile_id,
                                                  scheduler_id=scheduler_id,
                                                  vof=course_data['vof'])
        scheduler_profiles_list.append(scheduler_profile)
    
    # create everything
    Course.objects.bulk_create(courses)
    Schedule.objects.bulk_create(schedules.values())
    Scheduler.objects.bulk_create(schedulers.values())
    Scheduler.profiles.through.objects.bulk_create(scheduler_profiles_list, ignore_conflicts=True)
    
    # link courses
    linked_course_instances = []
    for course_instance in Scheduler.objects.all():
        if "*" in course_instance.course.hp and course_instance.schedule.period == 2:
            # get the matching scheduler objects 
            first_part = Scheduler.objects.get(course=course_instance.course,
                                               program=course_instance.program,
                                               schedule__period=1,
                                               schedule__semester=course_instance.schedule.semester
                                               )
            # linke them and add to list for bulk_update
            first_part.linked = course_instance
            course_instance.linked = first_part
            linked_course_instances.extend([first_part, course_instance])

    Scheduler.objects.bulk_update(linked_course_instances, ["linked"])

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

def register_course_details(data):
    examinations = []
    course_fields_list = []
    updated_courses = []
    create_fields = []
    
    for course_data in data:
        course_code = course_data["course_code"]
        for examination in course_data["examination"]:
            exam = Examination(
                code=examination["examination_code"],
                course_id=course_code,
                hp=examination["hp"],
                name=examination["name"],
                grading=examination["grading"]
            )
            examinations.append(exam)
        
        updated_course = Course.objects.filter(course_code=course_code)

        for field in course_data["main_field"]:
            main_field = MainField(field_name=field)
            course_fields = Course.main_fields.through(course_id=course_code, mainfield_id=main_field.field_name)
            course_fields_list.append(course_fields)
            create_fields.append(main_field)
            
        updated_course.update(examinator=course_data["examinator"])
        updated_course.update(campus=course_data["location"])
        
    MainField.objects.bulk_create(create_fields, ignore_conflicts=True) 
    Course.main_fields.through.objects.bulk_create(course_fields_list, ignore_conflicts=True)
    Examination.objects.bulk_create(examinations)
