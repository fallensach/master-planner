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
    account = Account.objects.get(user=request.user)
    
    try:
        scheduler = Scheduler.objects.get(scheduler_id=data.scheduler_id)
    except Scheduler.DoesNotExist:
        return 404, {"message": f"Could not find scheduler object: {data.scheduler_id} in scheduler table"}

    account.choices.add(scheduler)
    account.save()
                
    return 200, {"message": f"choice: {data.scheduler_id} has been added to account: {account.user.username}"}

@api.delete('account/choice', response={200: NoContent, 404: Error})
def choice(request, data: ChoiceSchema):
    
    account = Account.objects.get(user=request.user)
    
    try:
        scheduler = Scheduler.objects.get(scheduler_id=data.scheduler_id)
    except Scheduler.DoesNotExist:
        return 404, {"message": f"Could not find scheduler object: {data.scheduler_id} in scheduler table"}
    
    account.choices.remove(scheduler)
    account.save()
                
    return 200, {"message": f"choice: {data.scheduler_id} has been removed from account: {account.user.username}"}

@api.get('account/choice', response=List[SchedulerSchema])
def choice(request):
    account = Account.objects.get(user=request.user)
    return account.choices.all()

@api.get('get_course/{scheduler_id}', response={200: SchedulerSchema, 404: Error})
def get_course(request, scheduler_id):

    try:
        course_instance = Scheduler.objects.get(scheduler_id=scheduler_id)
    except Scheduler.DoesNotExist:
        return 404, {"message": f"Could not find scheduler object: {scheduler_id} in scheduler table"}

    return 200, course_instance

@api.get('courses/{profile}/{semester}', response=SemesterCourses)
def get_semester_courses(request, profile, semester):
    program = Account.objects.get(user=request.user).program
    

    period1 = Scheduler.objects.filter(program=program, 
                                       profile=profile, 
                                       schedule__semester=semester,
                                       schedule__period=1)
    period2 = Scheduler.objects.filter(program=program, 
                                       profile=profile, 
                                       schedule__semester=semester,
                                       schedule__period=2)
        
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
