from ninja import NinjaAPI, ModelSchema
from planning.models import Schedule
from django.core import serializers
from django.http import HttpResponse

api = NinjaAPI()

class ScheduleSchema(ModelSchema):
    class Config:
        model = Schedule
        model_fields = ["program_code", "course_code", "period", "semester", "block"]

@api.get('get_schedule/{schedule_id}', response=ScheduleSchema)
def res(request, schedule_id):
    schedule = Schedule.objects.get(schedule_id=schedule_id)
    return schedule