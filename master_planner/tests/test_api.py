
from django.test import TestCase
from planning.models import Scheduler, Schedule, Course, Program, Profile, MainField, Examination, register_courses, register_programs, register_profiles
from accounts.models import User, Account


class TestGetters(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username="test_user",  
                                        password="123",
                                        is_superuser=True,
                                        is_staff=True)
        account = Account.objects.create(user=user)

    def setUp(self):
        
        program_data = [("6CMJU", 'Civilingenjörsprogram i mjukvaruteknik'), 
                        ("6CDDD", 'Civilingenjörsprogram i datateknik')]
        profile_data = [("profile_1", "AAAA"), 
                        ("profile_2", "BBBB"), 
                        ("profile_3", "CCCC")]

        programs = register_programs(program_data)
        
        profiles = register_profiles(programs[0], profile_data[:2])
        profiles = register_profiles(programs[1], profile_data[1:])
        
        register_courses(programs[0], [{"course_code": "AAAA",
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
                                        }])
        user = Account.objects.get(user__username="test_user")
        user.program = programs[0]
        user.save()

        self.client.login(username="test_user", password="123")

    def test_courses(self):

        response = self.client.get('/api/courses/AAAA/7')

        self.assertEqual(response.status_code, 200)
        period_1 = response.json().get("period_1")
        period_2 = response.json().get("period_2")
        self.assertEqual(len(period_1), 2) 
        self.assertEqual(len(period_2), 0)
        response_data = period_1[0]

        def count(d):
            return sum([count(v) if isinstance(v, dict) else 1 for v in d.values()])
        
        self.assertEqual(count(response_data), 10)
        self.assertEqual(response_data["scheduler_id"], 1)
        self.assertEqual(response_data["program"], "6CMJU")
        self.assertEqual(response_data["schedule"]["semester"], 7)
        self.assertEqual(response_data["schedule"]["period"], 1)
        self.assertEqual(response_data["schedule"]["block"], "4")
        self.assertEqual(response_data["course"]["course_code"], "AAAA")
        self.assertEqual(response_data["course"]["course_name"], "test_course_1")
        self.assertEqual(response_data["course"]["hp"], "6")
        self.assertEqual(response_data["course"]["level"], "A1X")
        self.assertEqual(response_data["course"]["vof"], "v")

    def test_courses_wrong_parameters(self):
        response = self.client.get('/api/courses/WWWW/7')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get("period_1")), 0)
        self.assertEqual(len(response.json().get("period_2")), 0)

        response = self.client.get('/api/courses/AAAA/10')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get("period_1")), 0)
        self.assertEqual(len(response.json().get("period_2")), 0)

    def test_courses_not_logged_in(self):
        self.client.logout()

        response = self.client.get('/api/courses/AAAA/7')
        
        self.assertEqual(response.status_code, 401)
    
    # def test_course_details(self):
    #     course = Course.objects.get(course_code="AAAA")
    #     examination1 = Examination.objects.create(code="lab1",
    #                                               name="labb",
    #                                               hp="2",
    #                                               grading="u, g")
    #     examination2 = Examination.objects.create(code="lab2",
    #                                               name="labb",
    #                                               hp="2",
    #                                               grading="u, g")
    #     main_field1 = MainField.objects.create(field_name="Matematik")
    #     main_field2 = MainField.objects.create(field_name="nåttannat")
    #
    #     examination1.course = course
    #     examination2.course = course
    #     course.main_fields.add(main_field1)
    #     course.main_fields.add(main_field2)
    #     examination1.save()
    #     examination2.save()
    #     course.save()
    #
    #     response = self.client.get('/api/get_extra_course_info/AAAA')
    #     self.assertEqual(response.status_code, 200)
    #
    #     main_field_data = response.json().get("main_field")
    #     self.assertEqual(len(main_field), 2)
    #
    #     examination_data = response.json().get("examination")
    #     self.assertEqual(len(examination_data), 2)
    #
    #     self.assertEqual(examination_data[0]["code"], "lab1")
    #     self.assertEqual(examination_data[0]["name"], "labb")
    #     self.assertEqual(examination_data[0]["hp"], "2")
    #     self.assertEqual(examination_data[0]["grading"], "u, g")
    #     
    # def test_course_details_wrong_course_code(self):
    #
    #     response = self.client.get('/api/get_extra_course_info/WWWW')
    #     self.assertEqual(response.status_code, 400)

    def test_choices(self):
        response = self.client.get('/api/account/choices')

        self.assertEqual(response.status_code, 200)

    def test_choices_not_auth(self):
        self.client.logout()
        response = self.client.get('/api/account/choices')
        self.assertEqual(response.status_code, 400)

    def test_overview(self):
        response = self.client.get('/api/account/choices')

        self.assertEqual(response.status_code, 200)

    def test_overview_not_auth(self):
        self.client.logout()
        response = self.client.get('/api/account/choices')
        self.assertEqual(response.status_code, 400)










