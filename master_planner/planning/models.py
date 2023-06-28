from django.db import models
from planning.management.commands.scrappy.program_plan import ProgramPlan
from pprint import pprint
    

class Examination(models.Model):
    examination_id = models.IntegerField(primary_key=True)
    hp = models.CharField(max_length=5)
    name = models.CharField(max_length=50)
    grading = models.CharField(max_length=15)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class MainField(models.Model):
    field_name = models.CharField(max_length=15, primary_key=True)

    def __str__(self):
        return self.field_name

class Course(models.Model):
    course_code = models.CharField(max_length=6, primary_key=True)
    examinator = models.CharField(max_length=50, null=True, blank=True)
    examination = models.ForeignKey(Examination, blank=True, null=True, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=120)
    hp = models.CharField(max_length=5, default=1)
    level = models.CharField(max_length=20)
    vof = models.CharField(max_length=5)
    campus = models.CharField(max_length=20, blank=True, null=True)
    main_fields = models.ManyToManyField(MainField)

    def __str__(self):
        return self.course_code

class Schedule(models.Model):
    schedule_id = models.IntegerField(primary_key=True)
    period = models.IntegerField()
    semester = models.CharField(max_length=10)
    block = models.CharField(max_length=10)

    def __str__(self):
        return f"sem: {self.semester}, per: {self.period}, block: {self.block}"

class Profile(models.Model):
    profile_name = models.CharField(max_length=50)
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
    scheduler_id = models.IntegerField(primary_key=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{str(self.course_code)}\n{str(self.program)}\n{str(self.profile)}\n{str(self.schedule)}"

def register_program(program_code: str):
    program_exists = Program.objects.filter(program_code=program_code.upper()).exists()
    if not program_exists:
        
        program = ProgramPlan(program_code.upper())
        if program is None:
            return False
        courses = register_courses(program)
        register_profiles(program)
        add_courses(program, courses)
        program = ProgramPlan(program_code.upper())
        register_schedule(program)
    
    return True


def register_courses(program: ProgramPlan) -> list[Course]:
    general_courses = program.courses()
    courses = []
    
    for course in general_courses:
        new_course = Course(
                    course_code = course["course_code"], 
                    course_name = course["course_name"],
                    hp = course["hp"],
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
                hp = course["hp"],
                level = course["level"],
                vof = course["vof"],
            )
            profile_course.save()
            courses.append(profile_course)
            
        profile = Profile(name, code)
        new_program = Program(program.program_code, program.program_name)
        new_program.save()
        profile.save()
        profile.profile_courses.add(*courses)
        profile.save()
        new_program.program_profiles.add(profile)
        new_program.save()
    
def register_schedule(program: ProgramPlan):
    program_schedule = program.planned_courses()
    program_code = Program.objects.get(program_code=program.program_code)
    for semester in program_schedule:
        for term_name, terms in semester.items():
            for periods in terms:
                for period_name, courses in periods.items():
                    for course in courses:
                        db_course = Course.objects.get(course_code=course["course_code"])
                        block = course["block"]
                        if isinstance(block, int):
                            block = 0
                        schedule = Schedule(course_code=db_course, period=period_name[-1], semester=term_name, block=block, program_code=program_code)
                        schedule.save()


def add_courses(program: ProgramPlan, courses: list[Course]):
    program_add = Program.objects.get(program_code=program.program_code.upper())
    program_add.program_courses.add(*courses)
    program_add.save()
        
def get_courses(program_code: str):
    kurser = Program.objects.get(program_code=program_code.upper()).program_courses.all()
    courses = []
    for course in kurser:
        temp_course = { 
                    "course_code": course.course_code, 
                    "course_name": course.course_name,
                    "level": course.level,
                    "vof": course.vof
                    }
        courses.append(temp_course)
    return courses

def get_courses_term(program: str, term: str, profile_courses=None):
    if profile_courses != None:
        period_1 = Schedule.objects.filter(course_code__in=profile_courses, semester=term, period=1, program_code=program)
        period_2 = Schedule.objects.filter(course_code__in=profile_courses, semester=term, period=2, program_code=program)
    
    else:
        period_1 = Schedule.objects.filter(program_code=program, semester=term, period=1).all()
        period_2 = Schedule.objects.filter(program_code=program, semester=term, period=2).all()
    
    return make_schedule(period_1, period_2)
    
def make_schedule(period_1, period_2):
    schedule = {
        1: [],
        2: []
    }
    
    for period in period_1:
        scheduled_course = {period.schedule_id: {
            "course_code": period.course_code.course_code,
            "course_name": period.course_code.course_name,
            "hp": period.course_code.hp,
            "block": period.block,
            "vof": period.course_code.vof
             }
        }
        schedule[period.period].append(scheduled_course)
        
    for period in period_2:
        scheduled_course = {period.schedule_id: {
            "course_code": period.course_code.course_code,
            "course_name": period.course_code.course_name,
            "hp": period.course_code.hp,
            "block": period.block,
            "vof": period.course_code.vof
             }
        }
        schedule[period.period].append(scheduled_course)
    
    return schedule

    
