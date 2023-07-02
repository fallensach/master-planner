from ninja import NinjaAPI, ModelSchema
from django.http.response import JsonResponse
from planning.models import Schedule, Course, Scheduler
from planning.management.commands.scrappy.courses import fetch_course_info

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

# @api.get('')

@api.get('get_extra_course_info/{course_code}')
def get_extra_course_info(request, course_code):
    # extra_info = fetch_course_info(course_code)
    # course = Course.objects.get(course_code=course_code)
    # extra_info["course_code"] = course.course_code
    # extra_info["course_name"] = course.course_name
    return  {"examination": [{"code": "lab",
                              "name":  "laboration",
                              "scope": "6",
                              "grading": "u/g"}],
             "examinator": "cyrille",
             "location": "valla",
             "main_field": ["matematik"]
                }
    # return extra_info
