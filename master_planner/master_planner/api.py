from ninja import NinjaAPI, ModelSchema, Schema
from django.http.response import JsonResponse
from planning.models import Schedule, Course, Scheduler, Examination
from planning.management.commands.scrappy.courses import fetch_course_info
from accounts.models import get_user, Account
from typing import List
from .schemas import *

api = NinjaAPI()

@api.get('get_schedule/{schedule_id}', response=ScheduleSchema)
def get_schedule(request, schedule_id):
    schedule = Schedule.objects.get(schedule_id=schedule_id)
    return schedule

@api.get('account/overview')
def overview(request):
    pass

@api.post('account/choice', response={200: NoContent, 404: Error})
def choice(request, data: ChoiceSchema):
    print(data.scheduler_id)
    account = Account.objects.get(user__username="admin")
    
    # input()
    try:
        scheduler = Scheduler.objects.get(scheduler_id=data.scheduler_id)
    except Scheduler.DoesNotExist:
        return 404, {"message": "no scheduler object matching scheduler_id"}

    account.choices.add(scheduler)
    account.save()
                
    return 200, {"message": "all well"}

@api.delete('account/choice', response={200: NoContent, 404: Error})
def choice(request, data: ChoiceSchema):
    
    account = Account.objects.get(user__username="admin")
    
    try:
        scheduler = Scheduler.objects.get(scheduler_id=data.scheduler_id)
    except Scheduler.DoesNotExist:
        return 404, {"message": "Scheduler object doesnt exist in scheduler table"}
    #   fix error handling when there exists no matching choice
    #
    # try:
    #     choice = Account.objects.get(account=account)
    # except Scheduler.DoesNotExist:
    #     return 404, {"message": "User has no choice matching scheduler_id"}
    
    account.choices.remove(scheduler)
    account.save()
                
    return 200, {"message": "all well"}

@api.get('account/')
def choice(request, scheduler_id):
    account = Account.objects.get(user=request.user)

@api.get('get_course/{course_code}', response=CourseSchema)
def get_course(request, course_code):
    course_info = Course.objects.get(course_code=course_code)
    return course_info

@api.get('get_courses/{profile}/{semester}', response=SemesterCourses)
def get_semester_courses(request, profile, semester):
    program = Account.objects.get(user=request.user).program
    
    period1 = Scheduler.objects.filter(program=program, 
                                       profile=profile, 
                                       schedule__semester=f"Termin {semester}",
                                       schedule__period="Period 1")
    period2 = Scheduler.objects.filter(program=program, 
                                       profile=profile, 
                                       schedule__semester=f"Termin {semester}",
                                       schedule__period="Period 2")
        
    data = {"period_1": list(period1),
            "period_2": list(period2)}
    
    return data


@api.get('get_extra_course_info/{course_code}')
def get_extra_course_info(request, course_code):
    extra_info = fetch_course_info(course_code)
    course = Course.objects.get(course_code=course_code)
    extra_info["course_code"] = course.course_code
    extra_info["course_name"] = course.course_name
    """    
    return  {"examination": [{"code": "lab",
                              "name":  "laboration",
                              "scope": "6",
                              "grading": "u/g"}],
             "examinator": "cyrille",
             "location": "valla",
             "main_field": ["matematik"]
                }"""
    return extra_info
