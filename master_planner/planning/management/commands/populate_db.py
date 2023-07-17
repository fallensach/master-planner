from django.core.management.base import BaseCommand
from planning.management.commands.scrappy.program_plan import ProgramPlan
from planning.management.commands.scrappy.courses import fetch_course_info, fetch_programs
from planning.models import Course, Examination, MainField, Profile, Program, Schedule, Scheduler, register_profiles, register_courses, register_programs
from django.contrib.auth.models import User
from accounts.models import Account 
from planning.management.commands.scrappy.program_plan import ProgramPlan 
import threading


class Command(BaseCommand):
    help = 'our help string comes here'

    def add_arguments(self, parser):
        # Positional arguments
        #parser.add_argument("poll_ids", nargs="+", type=int)

        # Named (optional) arguments
        parser.add_argument(
            "--debug",
            action="store_true",
            help="only scrapes datateknik, mjukvaruteknik, tekniskt fysik",
        )

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

        account = Account(user=user, program=program)
        account.save()

        for semester in range(7, 10):
            for period in range(1, 3):
                for block in range(1, 5):
                    schedule = Schedule(semester=f"Termin {semester}", period=period, block=block)
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
                              course=course,
                              schedule=Schedule.objects.get(schedule_id=1),
                              program=program,
                              profile=profile
                              )        
        scheduler.save()

    def scrape_data(self, options):
        # fill Schedule
        # register_schedule()

        user = User.objects.create_user(username="admin",  
                                        password="123",
                                        is_superuser=True,
                                        is_staff=True)
        user.save()

        account = Account.objects.create(user=user)

        # fetch data and insert programs in db
        if options['debug']:
            program_data = [('6CMJU', 'Civilingenjörsprogram i mjukvaruteknik'), 
                            ('6CDDD', 'Civilingenjörsprogram i datateknik'),
                            ('6CYYY', 'Civilingenjörsprogram i teknisk fysik och elektroteknik')]
        else:
            print("start to fetch program data")
            program_data = fetch_programs()
        register_programs(program_data)
        
        course_data = []
        profile_data = []

        # scrape program data, add courses and profiles
        def extract_data(program_code):
            print(f"extracting course and profile data for {program_code}")
            prog_scraper = ProgramPlan(program_code)
            return prog_scraper.courses(), prog_scraper.profiles()

        def extract_data_thread(program_code):
            courses, profiles = extract_data(program_code)
            # Acquire a lock before modifying the shared lists
            with lock:
                course_data.extend(courses)
                profile_data.extend(profiles)

           # Create a lock to synchronize access to the shared lists
        lock = threading.Lock()

        # Create and start 17 threads
        threads = []
        for code, name in program_data:
            thread = threading.Thread(target=extract_data_thread, args=(code,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
       
        # for program_code, name in program_data:
        #     print(f"extracting course and profile data for {name}")
        #     prog_scraper = ProgramPlan(program_code)
        #     course_data.extend(prog_scraper.courses()) 
        #     profile_data.extend(prog_scraper.profiles())

        register_profiles(profile_data)
        register_courses(course_data)
        

    def handle(self, *args, **options):
        self.scrape_data(options)
