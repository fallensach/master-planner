from ninja import NinjaAPI, ModelSchema
from django.http.response import JsonResponse
from planning.models import Schedule, Course, Scheduler, get_courses_term
from planning.management.commands.scrappy.courses import fetch_course_info
from accounts.models import get_user, Account
from typing import List, Dict

api = NinjaAPI()

class SchedulerSchema(ModelSchema):
    class Config:
        model = Scheduler
        model_fields = ["program", "course", "schedule"]

class ScheduleSchema(ModelSchema):
    class Config:
        model = Schedule 
        model_fields = ["semester", "period", "block"]

class CourseSchema(ModelSchema):
    class Config:
        model = Course
        model_fields = ["course_code", "course_name", "hp", "level", "vof"]

@api.get('get_schedule/{schedule_id}', response=ScheduleSchema)
def get_schedule(request, schedule_id):
    schedule = Schedule.objects.get(schedule_id=schedule_id)
    return schedule

@api.get('get_course/{course_code}', response=CourseSchema)
def get_course(request, course_code):
    course_info = Course.objects.get(course_code=course_code)
    return course_info

@api.get('get_courses/{profile}/{semester}')
def get_semester_courses(request, profile, semester):
    program = Account.objects.get(user__username=request.user).program
    
#    period1 = Scheduler.objects.filter(program=program, 
#                                       profile=profile, 
#                                       schedule__semester=f"Termin {semester}",
#                                       schedule__period="Period 1")
#    period2 = Scheduler.objects.filter(program=program, 
#                                       profile=profile, 
#                                       schedule__semester=f"Termin {semester}",
#                                       schedule__period="Period 2")
    
    data = get_courses_term(program, f"Termin {semester}", profile)

    """    
    print(period1)

    data = {"period 1": period1,
            "period 2": period2}
    """
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
