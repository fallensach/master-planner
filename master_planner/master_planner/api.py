from ninja import NinjaAPI
from planning.models import Schedule, Course, Scheduler, Examination
from django.db.models import Sum, F, ExpressionWrapper, Case, When, Value, IntegerField
from django.db.models.functions import Cast, Replace
from planning.management.commands.scrappy.courses import fetch_course_info
from accounts.models import Account
from typing import List
from .schemas import *

api = NinjaAPI()

# @api.get('get_schedule/{schedule_id}', response=ScheduleSchema)
# def get_schedule(request, schedule_id):
#     schedule = Schedule.objects.get(schedule_id=schedule_id)
#     return schedule

@api.get('account/overview', response={200: NoContent, 401: Error})
def overview(request):
    if not request.user.is_authenticated:
        return 401, {"message": "authentication failed"}
    return 200, {"message": "placeholder"}

@api.post('account/choice', url_name="post_choice", response={200: LinkedScheduler, 406: Error, 401: Error})
def choice(request, data: ChoiceSchema):
    if not request.user.is_authenticated:
        return 401, {"message": "authentication failed"}
    account = Account.objects.get(user=request.user)
    
    try:
        scheduler = Scheduler.objects.get(scheduler_id=data.scheduler_id)
    except Scheduler.DoesNotExist:
        return 406, {"message": f"Could not find scheduler object in scheduler table"}

    account.choices.add(scheduler)
    account.save()
    
    if scheduler.linked:
        account.choices.add(scheduler.linked)
        account.save()
        return 200, {"scheduler_id": scheduler.linked.scheduler_id}
         
    return 200, {"scheduler_id": -1}
    

@api.delete('account/choice', url_name="delete_choice", response={200: LinkedScheduler, 406: Error, 401: Error})
def choice(request, data: ChoiceSchema):
    if not request.user.is_authenticated:
        return 401, {"message": "authentication failed"}
    account = Account.objects.get(user=request.user)
    
    try:
        scheduler = Scheduler.objects.get(scheduler_id=data.scheduler_id)
    except Scheduler.DoesNotExist:
        return 406, {"message": f"Could not find scheduler object in scheduler table"}
    
    account.choices.remove(scheduler)
    account.save()

    if scheduler.linked:
        account.choices.remove(scheduler.linked)
        account.save()
        return 200, {"scheduler_id": scheduler.linked.scheduler_id}
                    
    return 200, {"scheduler_id": -1}
    
@api.get('account/choices', response={200: Semesters, 401: Error})
def choice(request):
    if not request.user.is_authenticated:
        return 401, {"message": "authentication failed"}
    account = Account.objects.get(user=request.user)
    course_choices = {}
    total_hp = 0
    level_hp = account.level_hp()
   
    # sum hp for periods and semesters
    for semester in range(7, 10):
        semester_hp = 0
        periods = {}
        for period in range(1, 3):
            semester_period = account.choices.filter(schedule__semester=semester, schedule__period=period)
            period_hp = semester_period.aggregate(
                hp=Sum(
                    Case(
                        When(course__hp__endswith='*', then=Cast(F('course__hp'), IntegerField()) / 2),
                        default=Cast(F('course__hp'), IntegerField()),
                        output_field=IntegerField()
                        ),
                    output_field=IntegerField()
                    )
                )
            if period_hp["hp"] == None:
                period_hp["hp"] = 0

            periods[f"period_{period}"] = {"hp": {"total": period_hp["hp"], 
                                                  "a_level": level_hp[semester, period, "a_level"], 
                                                  "g_level": level_hp[semester, period, "g_level"]}, 
                                           "courses": list(semester_period)}

            semester_hp += period_hp["hp"]

        total_hp += semester_hp
        course_choices[f"semester_{semester}"] = {"hp": {"total": semester_hp,
                                                         "a_level": level_hp[semester, "a_level"], 
                                                         "g_level": level_hp[semester, "g_level"]}, 
                                                  "periods": periods}
    
    course_choices["hp"] = {"total": total_hp,
                            "a_level": level_hp["a_level"],
                            "g_level": level_hp["g_level"]
                            }
    return 200, course_choices

# @api.get('get_course/{scheduler_id}', response={200: SchedulerSchema, 404: Error})
# def get_course(request, scheduler_id):
#     try:
#         course_instance = Scheduler.objects.get(scheduler_id=scheduler_id)
#     except Scheduler.DoesNotExist:
#         return 404, {"message": f"Could not find scheduler object: {scheduler_id} in scheduler table"}
#
#     return 200, course_instance

@api.get('courses/{profile}/{semester}', response={200: SemesterCourses, 401: Error})
def get_semester_courses(request, profile, semester):
    if not request.user.is_authenticated:
        return 401, {"message": "authentication failed"}
    program = Account.objects.get(user=request.user).program
    

    period1 = Scheduler.objects.filter(program=program, 
                                       profiles=profile, 
                                       schedule__semester=semester,
                                       schedule__period=1)
    period2 = Scheduler.objects.filter(program=program, 
                                       profiles=profile, 
                                       schedule__semester=semester,
                                       schedule__period=2)
        
    data = {"period_1": list(period1),
            "period_2": list(period2)}
    
    return 200, data


@api.get('get_extra_course_info/{course_code}', response={200: ExaminationDetails, 401: Error})
def get_extra_course_info(request, course_code):
    if not request.user.is_authenticated:
        return 401, {"message": "Unauthorized access"}

    course = Course.objects.get(course_code=course_code)
    main_fields = course.main_fields.all()
    examination = Examination.objects.filter(course=course).all()
    data = {"examinations": [], 
            "main_fields": [],
            "examinator": course.examinator,
            "location": course.campus,
            "course": course
            }

    for field in list(main_fields):
        data["main_fields"].append(field.field_name)
    
    for exam in list(examination):
        data["examinations"].append(exam)
        
    return data

"""    
return  {"examination": [{"code": "lab",
                            "name":  "laboration",
                            "scope": "6",
                            "grading": "u/g"}],
            "examinator": "cyrille",
            "location": "valla",
            "main_field": ["matematik"]
            }"""
