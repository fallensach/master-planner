from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from planning.models import Schedule, Course, Scheduler, Examination
from planning.management.commands.scrappy.courses import fetch_course_info
from typing import List, Union

class ScheduleSchema(ModelSchema):
    class Config:
        model = Schedule 
        model_fields = ["block", "semester", "period"]

class CourseSchema(ModelSchema):
    class Config:
        model = Course
        model_fields = ["course_code", "course_name", "hp", "level", "vof"]
        
class SchedulerSchema(ModelSchema):
    course: CourseSchema
    schedule: ScheduleSchema
    class Config:
        model = Scheduler
        model_fields = ["scheduler_id", "program", "schedule"]

class SemesterCourses(Schema):
    period_1: List[SchedulerSchema]
    period_2: List[SchedulerSchema]

class MySchedulerSchema(ModelSchema):
    course: CourseSchema
    schedule: ScheduleSchema
    class Config:
        model = Scheduler
        model_fields = ["scheduler_id", "program", "schedule"]

class HpSchema(Schema):
    total: int
    a_level: int
    g_level: int

class MyCourseSchema(Schema):
    hp: HpSchema
    courses: List[SchedulerSchema]

class MyPeriodSchema(Schema):
    period_1: MyCourseSchema
    period_2: MyCourseSchema

class MySemesterCourses(Schema):
    hp: HpSchema
    periods: MyPeriodSchema

# class TestHpSchema(Schema):
#     (7, 1, "a_lever"): int
#     (7, 2, "g_level"): int
#     (7, 1, "total"): int

class Semesters(Schema):
    hp: HpSchema
    semester_7: MySemesterCourses
    semester_8: MySemesterCourses
    semester_9: MySemesterCourses

class ExaminationSchema:
    class Config:
        model = Examination
        model_fields = []
class ChoiceSchema(Schema):
    scheduler_id: int

class Error(Schema):
    message: str 
    
class LinkedScheduler(Schema):
    scheduler_id: int

class NoContent(Schema):
    message: str
