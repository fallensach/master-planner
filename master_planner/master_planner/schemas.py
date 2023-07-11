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

class MyCourseSchema(Schema):
    hp: int
    courses: List[SchedulerSchema]

class MyPeriodSchema(Schema):
    period_1: MyCourseSchema
    period_2: MyCourseSchema

class MySemesterCourses(Schema):
    hp: int
    periods: MyPeriodSchema

class Semesters(Schema):
    hp: int
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

class NoContent(Schema):
    message: str
