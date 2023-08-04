from ninja import ModelSchema, Schema, Field
from ninja.orm import create_schema
from planning.models import Schedule, Course, Scheduler, Examination, SchedulersProfiles
from planning.management.commands.scrappy.courses import fetch_course_info
from typing import List, Dict
import uuid


class ScheduleSchema(ModelSchema):
    class Config:
        model = Schedule 
        model_fields = ["block", "semester", "period"]

class CourseSchema(ModelSchema):
    class Config:
        model = Course
        model_fields = ["course_code", "course_name", "hp", "level", "examinator"]
        
class SchedulerSchema(ModelSchema):
    course: CourseSchema
    schedule: ScheduleSchema

    class Config:
        model = Scheduler
        model_fields = ["scheduler_id"]

class ExtendedSchedulerSchema(ModelSchema):
    scheduler_id: uuid.UUID = Field(..., alias="scheduler.scheduler_id")
    course: CourseSchema = Field(..., alias="scheduler.course")
    schedule: ScheduleSchema = Field(..., alias="scheduler.schedule")
    class Config:
        model = SchedulersProfiles
        model_fields = ["vof"]

class SemesterCourses(Schema):
    period_1: List[ExtendedSchedulerSchema]
    period_2: List[ExtendedSchedulerSchema]



class MySchedulerSchema(ModelSchema):
    course: CourseSchema
    schedule: ScheduleSchema
    class Config:
        model = Scheduler
        model_fields = ["scheduler_id", "program", "schedule"]

class ExaminationSchema(ModelSchema):
    class Config:
        model = Examination
        model_fields = ["hp", "name", "grading", "code"] 

class ExaminationDetails(Schema):
    examinations: List[ExaminationSchema]
    examinator: str
    location: str
    main_fields: List[str]
    course: CourseSchema

class HpSchema(Schema):
    total: int
    a_level: int
    g_level: int

class MyCourseSchema(Schema):
    hp: HpSchema
    courses: List[ExtendedSchedulerSchema]

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
    scheduler_id: uuid.UUID

class Error(Schema):
    message: str 
    
class LinkedScheduler(Schema):
    scheduler_id: int

class PeriodSchema(Schema):
    period_1: HpSchema
    period_2: HpSchema

class SemesterOverviewSchema(Schema):
    overlap: List[List[SchedulerSchema]]
    periods: PeriodSchema
    hp: HpSchema

class OverviewSchema(Schema):
    total_hp: int
    a_level: int
    g_level: int
    field: Dict[str, int]
    profile: Dict[str, int]
    semester_7: SemesterOverviewSchema
    semester_8: SemesterOverviewSchema
    semester_9: SemesterOverviewSchema



class NoContent(Schema):
    message: str
