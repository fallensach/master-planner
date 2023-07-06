from ninja import NinjaAPI, ModelSchema, Schema
from django.http.response import JsonResponse
from planning.models import Schedule, Course, Scheduler, Examination
from planning.management.commands.scrappy.courses import fetch_course_info
from accounts.models import get_user, Account
from typing import List

class ScheduleSchema(ModelSchema):
    class Config:
        model = Schedule 
        model_fields = ["block", "semester", "period"]

class CourseSchema(ModelSchema):
    class Config:
        model = Course
        model_fields = ["course_code", "course_name", "hp", "level", "vof"]

class ExaminationSchema:
    class Config:
        model = Examination
        model_fields = []

# class CourseDetailSchema(ModelSchema):
#     examination: ExaminationSchema
#     class Config:
#         model = Course
#         model_fields = []

class SchedulerSchema(ModelSchema):
    course: CourseSchema
    schedule: ScheduleSchema
    class Config:
        model = Scheduler
        model_fields = ["scheduler_id", "program", "schedule"]

class SemesterCourses(Schema):
    period_1: List[SchedulerSchema]
    period_2: List[SchedulerSchema]

class ChoiceSchema(Schema):
    scheduler_id: int

class Error(Schema):
    message: str 

class NoContent(Schema):
    message: str
