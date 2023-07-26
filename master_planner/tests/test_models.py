from django.test import TestCase
from planning.models import Scheduler, Schedule, Course, Program, Profile, MainField, Examination, register_courses, register_programs, register_profiles
from accounts.models import User, Account


class TestModelsPlanning(TestCase):
    
    @classmethod
    def setUpTestData(cls): 
        pass

    def setUp(self):
        self.program_data = [("6CMJU", 'Civilingenjörsprogram i mjukvaruteknik'), 
                             ("6CDDD", 'Civilingenjörsprogram i datateknik')]

        self.profile_data = [("profile_1", "AAAA", "6CMJU"), 
                             ("profile_2", "BBBB", "6CMJU"), 
                             ("profile_3", "CCCC", "6CMJU"),
                             ("profile_1", "AAAA", "6CDDD"), 
                             ("profile_2", "BBBB", "6CDDD"), 
                             ("profile_3", "CCCC", "6CDDD")]
        
        self.course_data = [{"course_code": "AAAA",
                             "course_name": "test_course_1",
                             "program_code": "6CMJU",
                             "hp": "6",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 1,
                             "semester": 7
                             },
                            {"course_code": "BBBB",
                             "program_code": "6CMJU",
                             "course_name": "test_course_2",
                             "hp": "6",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 1,
                             "semester": 7
                             },
                            {"course_code": "CCCC",
                             "course_name": "test_course_3",
                             "program_code": "6CMJU",
                             "hp": "6*",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 1,
                             "semester": 7
                             },
                            {"course_code": "CCCC",
                             "course_name": "test_course_3",
                             "hp": "6*",
                             "program_code": "6CMJU",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 2,
                             "semester": 7
                             },
                            {"course_code": "AAAA",
                             "course_name": "test_course_1",
                             "program_code": "6CDDD",
                             "hp": "6",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 1,
                             "semester": 7
                             },
                            {"course_code": "BBBB",
                             "program_code": "6CDDD",
                             "course_name": "test_course_2",
                             "hp": "6",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 1,
                             "semester": 7
                             },
                            {"course_code": "CCCC",
                             "course_name": "test_course_3",
                             "program_code": "6CDDD",
                             "hp": "6*",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 1,
                             "semester": 7
                             },
                            {"course_code": "CCCC",
                             "course_name": "test_course_3",
                             "hp": "6*",
                             "program_code": "6CDDD",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 2,
                             "semester": 7
                             }]
        

    def test_register_programs(self):
        register_programs(self.program_data)
        
        programs = Program.objects.all()
        program_count = len(self.program_data)

        self.assertEqual(programs.count(), program_count)

       # register_programs(self.program_data)
        # 
        # programs = Program.objects.all()
        #
        # self.assertEqual(programs.count(), program_count)

            
    def test_register_profiles(self):
        self.test_register_programs()
        program = Program.objects.get(program_code="6CMJU") 
        profile_count = 3
        
        # regular insert
        register_profiles(self.profile_data)
        self.assertEqual(program.profiles.count(), profile_count)

        # # same profiles for another program
        program = Program.objects.get(program_code="6CDDD")
        self.assertEqual(program.profiles.count(), profile_count)
    
    def test_register_courses(self):
        # init
        self.test_register_profiles()
        program = Program.objects.get(program_code="6CMJU")
        course_instances_count = len(self.course_data)
       
        # function to be tested
        register_courses(self.course_data)
        
        # assert right number have been inserted
        self.assertEqual(Scheduler.objects.count(), course_instances_count)

        # # assert right number have been linked
        # linked = Scheduler.objects.filter().exclude(linked__isnull=True)
        # self.assertEqual(linked.count(), 2)
        #
        # # assert right courses has been linked
        # first = linked[0]
        # second = linked[1]
        # self.assertEqual(first.linked, second)
        # self.assertEqual(second.linked, first)
        # 
        # another_course = [{"course_code": "AAAA",
        #                    "course_name": "test_course_1",
        #                    "hp": "6",
        #                    "level": "A1X",
        #                    "block": 4,
        #                    "vof": "v",
        #                    "profile_code": "BBBB",
        #                    "period" : 1,
        #                    "semester": 7
        #                    }]
        # register_courses(program, another_course)
        #
        # self.assertEqual(Scheduler.objects.get(program=program, course="AAAA").profiles.count(), 2)


class TestModelsAccounts(TestCase):
    
    @classmethod
    def setUpTestData(cls): 
        user = User.objects.create_user(username="test_user",  
                                        password="123",
                                        is_superuser=True,
                                        is_staff=True)
        account = Account.objects.create(user=user)

        profile_1 = Profile.objects.create(profile_code="AAAA",
                                           profile_name="Profile 1")
        profile_2 = Profile.objects.create(profile_code="BBBB",
                                           profile_name="Profile 2")
        program = Program.objects.create(program_code="6CMJU",
                                         program_name="Program 1")
        program.profiles.add(profile_1)
        program.profiles.add(profile_2)
        program.save()

        # creating two course instances with different scheudles and profiles
        course_1 = Course.objects.create(course_code="aaaa",
                                         course_name="course 1",
                                         hp="10",
                                         level="A1X",
                                         vof="v")
        schedule_1 = Schedule.objects.create(semester=7,
                                             period=1,
                                             block=3)
        course_instance_1 = Scheduler.objects.create(program=program,
                                                     course=course_1,
                                                     schedule=schedule_1,
                                                     )
        course_instance_1.profiles.add(profile_1)
        course_instance_1.save()
        
        course_2 = Course.objects.create(course_code="bbbb",
                                         course_name="course 2",
                                         hp="10",
                                         level="G1X",
                                         vof="v")
        schedule_2 = Schedule.objects.create(semester=9,
                                             period=2,
                                             block=1)
        course_instance_2 = Scheduler.objects.create(program=program,
                                                     course=course_2,
                                                     schedule=schedule_2,
                                                     )
        course_instance_2.profiles.add(profile_2)
        course_instance_2.save()

        # two linked courses (spans two periods)
        course_3 = Course.objects.create(course_code="cccc",
                                         course_name="course 3",
                                         hp="10*",
                                         level="A1X",
                                         vof="v")
        schedule_3 = Schedule.objects.create(semester=9,
                                             period=1,
                                             block=1)
        course_instance_3 = Scheduler.objects.create(program=program,
                                                     course=course_3,
                                                     schedule=schedule_3,
                                                     )
        course_instance_3.profiles.add(profile_1)
        course_instance_3.profiles.add(profile_2)
        course_instance_3.save()

        schedule_4 = Schedule.objects.create(semester=9,
                                             period=2,
                                             block=4)
        course_instance_4 = Scheduler.objects.create(program=program,
                                                     course=course_3,
                                                     schedule=schedule_4,
                                                     )
        course_instance_4.profiles.add(profile_1)
        course_instance_4.profiles.add(profile_2)
        course_instance_4.save()
        course_instances = [course_instance_1.scheduler_id,
                             course_instance_2.scheduler_id,
                             course_instance_3.scheduler_id,
                             course_instance_4.scheduler_id
                             ]
        for ci in course_instances:
            account.choices.add(ci)
            account.save()

    def setUp(self):
        self.client.login(username="test_user", password="123")

                
    def test_level_hp(self):
        account = Account.objects.get(user__username="test_user")

        level_hp = account.level_hp()

        self.assertEqual(level_hp[7, 1, "a_level"], 10.0)
        self.assertEqual(level_hp[7, "a_level"], 10.0)
        self.assertEqual(level_hp[9, 1, "a_level"], 5.0)
        self.assertEqual(level_hp[9, 2, "a_level"], 5.0)
        self.assertEqual(level_hp[9, 2, "g_level"], 10.0)
        self.assertEqual(level_hp[9, "g_level"], 10.0)
        self.assertEqual(level_hp[9, "a_level"], 10.0)
        self.assertEqual(level_hp["a_level"], 20.0)
        self.assertEqual(level_hp["g_level"], 10.0)
















