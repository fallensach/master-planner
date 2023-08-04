from ninja import NinjaAPI
from planning.models import Schedule, Course, Scheduler, Examination, SchedulersProfiles
from planning.models import Schedule, Course, Scheduler
from django.db.models import Sum, F, Q, ExpressionWrapper, Case, When, Value, IntegerField, Count
from django.db.models.functions import Cast, Replace, Substr
from planning.management.commands.scrappy.courses import fetch_course_info
from accounts.models import Account
from typing import List
from .schemas import *
from functools import reduce
from operator import or_
import pprint

api = NinjaAPI()

@api.get("account/overview", response={200: OverviewSchema, 401: Error})
def overview(request):
    if not request.user.is_authenticated:
        return 401, {"message": "authentication failed"}

    account_instance = Account.objects.select_related("program").get(user=request.user)

    total_hp_by_mainfield = (account_instance.choices
                             .values_list("course__main_fields__field_name")
                             .distinct()
                             .annotate(total_hp=Sum(
                                                    Case(
                                                        When(course__hp__endswith="*", 
                                                             then=Cast(F("course__hp"), IntegerField()) / 2
                                                             ),
                                                        default=Cast(F("course__hp"), IntegerField()),
                                                        output_field=IntegerField()
                                                        ),
                                                    output_field=IntegerField()
                                                    )
                                       )
                             )
    total_hp_by_mainfield = dict(total_hp_by_mainfield)

    distinct_scheduler_ids = account_instance.choices.values_list("scheduler_id").distinct()
    distinct_course_codes = account_instance.choices.values_list("course_id").distinct()
    print("scheduler:", distinct_scheduler_ids)
    print("course:", distinct_course_codes)

    filtered_choices = (Scheduler
                        .objects
                        .filter(scheduler_id__in=distinct_scheduler_ids,
                                program=account_instance.program)
                        .values_list("profiles")
                        .distinct()
                       )
    print("filter", filtered_choices)
    
    total_hp_by_profile = (Scheduler
                           .objects
                           .filter(course_id__in=distinct_course_codes,
                                   program=account_instance.program
                                   )
                           .exclude(~Q(scheduler_id__in=distinct_scheduler_ids),
                                       profiles__in=filtered_choices)
                           .values_list("profiles__profile_name")
                           .distinct()
                           .annotate(total_hp=Sum(
                                                  Case(
                                                      When(course__hp__endswith="*", 
                                                           then=Cast(F("course__hp"), IntegerField()) / 2
                                                           ),
                                                      default=Cast(F("course__hp"), IntegerField()),
                                                      output_field=IntegerField()
                                                      ),
                                                  output_field=IntegerField()
                                                  )
                                     )
                           )
    total_hp_by_profile = dict(total_hp_by_profile)
    if "Ingen profil" in total_hp_by_profile:
        del total_hp_by_profile["Ingen profil"]

    overlapping_schedules = (account_instance.choices
                             .values("schedule__semester", "schedule__period", "schedule__block")
                             .annotate(count=Count("scheduler_id"))
                             .filter(count__gt=1)
                             )
    
    if overlapping_schedules:


        query = reduce(or_, (Q(schedule__semester=schedule["schedule__semester"],
                               schedule__period=schedule["schedule__period"],
                               schedule__block=schedule["schedule__block"]) for schedule in overlapping_schedules)) 

        overlapping_choices = (account_instance
                               .choices
                               .filter(query)
                               .order_by("schedule")
                               .values_list("schedule__semester",
                                            "schedule__period",
                                            "schedule__block",
                                            "scheduler_id")
                               )

        overlapping_dict = {7: {}, 8: {}, 9: {}}
        # for scheduler_instance in overlapping_choices:
        #     overlapping_dict[scheduler_instance.schedule.semester].append(scheduler_instance)
        for sem, *period_block, scheduler_id in overlapping_choices:
            period_block = tuple(period_block)
            if period_block in overlapping_dict[sem]:
                overlapping_dict[sem][period_block].append(Scheduler.objects.get(scheduler_id=scheduler_id))
            else:
                overlapping_dict[sem].update({period_block: [Scheduler.objects.get(scheduler_id=scheduler_id)]})
        
        for sem, courses in overlapping_dict.items():
            overlapping_dict[sem] = list(courses.values())



    else:
        overlapping_dict = {7: [], 8: [], 9: []}
    

    level_hp = account_instance.level_hp()
    response = {"field": total_hp_by_mainfield,
                "profile": total_hp_by_profile,
                "total_hp": level_hp["a_level"]+level_hp["g_level"],
                "a_level": level_hp["a_level"],
                "g_level": level_hp["g_level"]
                }

    for semester in range(7, 10):
        periods = {}
        for period in range(1, 3):
            total_hp_in_period = level_hp[semester, period, "a_level"]+level_hp[semester, period, "g_level"]

            periods[f"period_{period}"] = {"total": total_hp_in_period, 
                                           "a_level": level_hp[semester, period, "a_level"], 
                                           "g_level": level_hp[semester, period, "g_level"]}

        total_hp_in_semester = level_hp[semester, "a_level"]+level_hp[semester, "g_level"]
        response[f"semester_{semester}"] = {"overlap": overlapping_dict[semester],
                                            "hp": {"total": total_hp_in_semester,
                                                   "a_level": level_hp[semester, "a_level"],
                                                   "g_level": level_hp[semester, "g_level"]
                                                   },
                                            "periods": periods
                                            }
    return 200, response

@api.post("account/choice", url_name="post_choice", response={200: LinkedScheduler, 406: Error, 401: Error})
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
    

@api.delete("account/choice", url_name="delete_choice", response={200: LinkedScheduler, 406: Error, 401: Error})
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
    
@api.get("account/choices/{profile_code}", response={200: Semesters, 401: Error})
def choice(request, profile_code):
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
            choices = account.choices.filter(schedule__semester=semester, schedule__period=period)
            period_hp = choices.aggregate(
                hp=Sum(
                    Case(
                        When(course__hp__endswith="*", then=Cast(F("course__hp"), IntegerField()) / 2),
                        default=Cast(F("course__hp"), IntegerField()),
                        output_field=IntegerField()
                        ),
                    output_field=IntegerField()
                    )
                )
            if profile_code == "free":
                choices_vof = SchedulersProfiles.objects.filter(scheduler__in=choices,
                                                                profile_id=profile_code,
                                                                scheduler__schedule__semester=semester,
                                                                scheduler__schedule__period=period)
            else:
                profile_choices = SchedulersProfiles.objects.values_list("scheduler").filter(scheduler__in=choices,
                                                                         profile_id=profile_code, 
                                                                         scheduler__schedule__semester=semester,
                                                                         scheduler__schedule__period=period)                                   
                          
                choices_vof = SchedulersProfiles.objects.filter(Q(scheduler__in=choices,
                                                                  profile_id=profile_code, 
                                                                  scheduler__schedule__semester=semester,
                                                                  scheduler__schedule__period=period
                                                                  )
                                                                |
                                                                Q(scheduler__in=choices,
                                                                    profile_id="free", 
                                                                    scheduler__schedule__semester=semester,
                                                                    scheduler__schedule__period=period
                                                                    )
                                                                ).exclude(scheduler__in=profile_choices,
                                                                           profile_id="free")

            if period_hp["hp"] == None:
                period_hp["hp"] = 0
            
            periods[f"period_{period}"] = {"hp": {"total": period_hp["hp"], 
                                                  "a_level": level_hp[semester, period, "a_level"], 
                                                  "g_level": level_hp[semester, period, "g_level"]}, 
                                           "courses": list(choices_vof)}

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

@api.get("courses/{profile}/{semester}", response={200: SemesterCourses, 401: Error})
def get_semester_courses(request, profile, semester):
    if not request.user.is_authenticated:
        return 401, {"message": "authentication failed"}
    program = Account.objects.get(user=request.user).program
    

    period1 = SchedulersProfiles.objects.filter(scheduler__program=program, 
                                       profile=profile, 
                                       scheduler__schedule__semester=semester,
                                       scheduler__schedule__period=1)
    period2 = SchedulersProfiles.objects.filter(scheduler__program=program, 
                                       profile=profile, 
                                       scheduler__schedule__semester=semester,
                                       scheduler__schedule__period=2)
    
    data = {"period_1": list(period1),
            "period_2": list(period2)}
    # print(data)
    return 200, data

@api.get("get_extra_course_info/{course_code}", response={200: ExaminationDetails, 401: Error})
def get_extra_course_info(request, course_code):
    if not request.user.is_authenticated:
        return 401, {"message": "Unauthorized access"}

    course = Course.objects.get(course_code=course_code)
    main_fields = course.main_fields.all().values_list("field_name", flat=True)
    examination = Examination.objects.filter(course=course).all()

    data = {"examinations": list(examination), 
            "main_fields": list(main_fields),
            "examinator": course.examinator,
            "location": course.campus,
            "course": course
            }

    return data
