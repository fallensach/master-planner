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

        self.profile_data = [("profile_1", "AAAA"), 
                             ("profile_2", "BBBB"), 
                             ("profile_3", "CCCC")]
        
        self.course_data = [{"course_code": "AAAA",
                             "course_name": "test_course_1",
                             "hp": "6",
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 1,
                             "semester": 7
                             },
                            {"course_code": "BBBB",
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
                             "level": "A1X",
                             "block": 4,
                             "vof": "v",
                             "profile_code": "AAAA",
                             "period" : 1,
                             "semester": 7
                             }]
        

    def test_register_programs(self):
        register_programs(self.program_data)
        
        programs = Program.objects.all()
        program_count = len(self.program_data)

        self.assertEqual(programs.count(), program_count)

        register_programs(self.program_data)
        
        programs = Program.objects.all()

        self.assertEqual(programs.count(), program_count)

            
    def test_register_profiles(self):
        self.test_register_programs()
        
        program = Program.objects.get(program_code="6CMJU")
        profile_count = len(self.profile_data)
        
        # regular insert
        register_profiles(program, self.profile_data)
        self.assertEqual(program.profiles.count(), profile_count)
        
        # double insert
        register_profiles(program, self.profile_data)
        self.assertEqual(program.profiles.count(), profile_count)
        
        # same profiles for another program
        program = Program.objects.get(program_code="6CDDD")
        profile_count = len(self.profile_data)
        
        register_profiles(program, self.profile_data)
        self.assertEqual(Profile.objects.count(), profile_count)
    
    def test_register_courses(self):
        self.test_register_programs()
        self.test_register_profiles()
        program = Program.objects.get(program_code="6CMJU")
        course_instances_count = len(self.course_data)
        register_courses(program, self.course_data)
        print(Scheduler.objects.all())
        self.assertEqual(Scheduler.objects.count(), course_instances_count)
        self.assertEqual(Scheduler.objects.filter().exclude(linked=null).count(), 2)


class TestModelsAccounts(TestCase):
    
    @classmethod
    def setUpTestData(cls): 
        pass

    def setUp(self):
        pass


