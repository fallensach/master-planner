from django.core.management.base import BaseCommand
from planning.management.commands.scrappy.program_plan import ProgramPlan
from planning.management.commands.scrappy.courses import fetch_course_info
from planning.models import Course, Examination, MainField, Profile, Program, Schedule, Scheduler
from django.contrib.auth.models import User
from accounts.models import Account 


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def add_data(self):
        program = Program(program_name="mjukvaruteknik", 
                          program_code="6cmju")
        program.save()
        profile = Profile(profile_name="ai", 
                          profile_code="daim")
        profile.save()
        program.profiles.add(profile)
        program.save()

        user = User.objects.create_user(username="admin",  
                                        password="123",
                                        is_superuser=True,
                                        is_staff=True)
        user.save()

        account = Account(user=user, program_code=program)
        account.save()

        for semester in range(7, 10):
            for period in range(1, 3):
                for block in range(1, 5):
                    schedule = Schedule(semester=semester, period=period, block=block)
                    schedule.save()

        examination = Examination(examination_id=1,
                                  hp="6", 
                                  name="laboration", 
                                  grading="u/g", 
                                  code="lab1")
        examination.save()

        field = MainField(field_name="Matematik")
        field.save()

        course = Course(course_code="tata24",
                        course_name="linjär algebra",
                        hp="6",
                        examinator="cyrille berger",
                        level="advanced",
                        vof="o",
                        campus="valla",
                        examination=examination
                        )
        course.save() 
        course.main_fields.add(field)
        course.save()

        scheduler = Scheduler(scheduler_id=1,
                              course_code=course,
                              schedule=Schedule.objects.get(schedule_id=1),
                              program=program,
                              profile=profile
                              )        
        scheduler.save()





    def handle(self, *args, **options):
        self.add_data()
