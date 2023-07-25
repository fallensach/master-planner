from django.urls import reverse
from django.test import TestCase
from planning.models import Scheduler, Schedule, Course, Program, Profile, MainField, Examination, register_courses, register_programs, register_profiles
from accounts.models import User, Account
import json
import uuid


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
        profile_data = [("profile_1", "AAAA", "6CMJU"), 
                        ("profile_2", "BBBB", "6CMJU"), 
                        ("profile_3", "CCCC", "6CDDD")]

        # programs = register_programs(program_data)
        prog_1 = Program.objects.create(program_name="mjukvaruteknik", program_code="6CMJU")
        prog_2 = Program.objects.create(program_name="datateknik", program_code="6CDDD")
        
        profile_1 = Profile.objects.create(profile_name="profile_1", profile_code="AAAA")
        profile_2 = Profile.objects.create(profile_name="profile_2", profile_code="BBBB")
        prog_1.profiles.add(profile_1)
        prog_1.profiles.add(profile_2)
        prog_1.save()

        profile_3 = Profile.objects.create(profile_name="profile_3", profile_code="CCCC")
        prog_2.profiles.add(profile_3)
        prog_2.save()
        
        register_courses([{"course_code": "AAAA",
                           "course_name": "test_course_1",
                           "hp": "6",
                           "program_code": "6CMJU",
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
                           "program_code": "6CMJU",
                           "level": "A1X",
                           "block": 4,
                           "vof": "v",
                           "profile_code": "AAAA",
                           "period" : 1,
                           "semester": 7
                           }])
        account = Account.objects.get(user__username="test_user")
        account.program = prog_1
        account.save()

        self.client.login(username="test_user", password="123")

    def test_courses(self):

        response = self.client.get('/api/courses/AAAA/7')

        self.assertEqual(response.status_code, 200)
        period_1 = response.json().get("period_1")
        period_2 = response.json().get("period_2")
        self.assertEqual(len(period_1), 2) 
        self.assertEqual(len(period_2), 0)
        response_data = period_1[0]

        # def count(d):
        #     return sum([count(v) if isinstance(v, dict) else 1 for v in d.values()])
        # 
        # self.assertEqual(count(response_data), 10)
        # self.assertEqual(response_data["scheduler_id"], 1)
        # self.assertEqual(response_data["program"], "6CMJU")
        # self.assertEqual(response_data["schedule"]["semester"], 7)
        # self.assertEqual(response_data["schedule"]["period"], 1)
        # self.assertEqual(response_data["schedule"]["block"], "4")
        # self.assertEqual(response_data["course"]["course_code"], "AAAA")
        # self.assertEqual(response_data["course"]["course_name"], "test_course_1")
        # self.assertEqual(response_data["course"]["hp"], "6")
        # self.assertEqual(response_data["course"]["level"], "A1X")
        # self.assertEqual(response_data["course"]["vof"], "v")

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

    def test_choices(self):
        response = self.client.get('/api/account/choices')

        self.assertEqual(response.status_code, 200)

    def test_choices_not_auth(self):
        self.client.logout()
        response = self.client.get('/api/account/choices')
        self.assertEqual(response.status_code, 401)

    def test_overview(self):
        response = self.client.get('/api/account/choices')

        self.assertEqual(response.status_code, 200)

    def test_overview_not_auth(self):
        self.client.logout()
        response = self.client.get('/api/account/choices')
        self.assertEqual(response.status_code, 401)

class TestPosters(TestCase):
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
        profile_data = [("profile_1", "AAAA", "6CMJU"), 
                        ("profile_2", "BBBB", "6CMJU"), 
                        ("profile_3", "CCCC", "6CDDD")]

        # programs = register_programs(program_data)
        prog_1 = Program.objects.create(program_name="mjukvaruteknik", program_code="6CMJU")
        prog_2 = Program.objects.create(program_name="datateknik", program_code="6CDDD")
        
        profile_1 = Profile.objects.create(profile_name="profile_1", profile_code="AAAA")
        profile_2 = Profile.objects.create(profile_name="profile_2", profile_code="BBBB")
        prog_1.profiles.add(profile_1)
        prog_1.profiles.add(profile_2)
        prog_1.save()

        profile_3 = Profile.objects.create(profile_name="profile_3", profile_code="CCCC")
        prog_2.profiles.add(profile_3)
        prog_2.save()
        
        register_courses([{"course_code": "AAAA",
                           "course_name": "test_course_1",
                           "hp": "6",
                           "program_code": "6CMJU",
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
                           "program_code": "6CMJU",
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
                           }])
        account = Account.objects.get(user__username="test_user")
        account.program = prog_1
        account.save()
        self.account = account

        self.client.login(username="test_user", password="123")

    def test_choice(self):
        course_instance = Scheduler.objects.all()[0]
        data = {"scheduler_id": course_instance.scheduler_id}
        response = self.client.post(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("scheduler_id"), -1)
        self.assertEqual(self.account.choices.count(), 1)

    def test_choice_linked(self):
        course_instance_1 = Scheduler.objects.get(course__course_code="CCCC", schedule__period=1)
        course_instance_2 = Scheduler.objects.get(course__course_code="CCCC", schedule__period=2)
        
        data = {"scheduler_id": course_instance_1.scheduler_id}
        response = self.client.post(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("scheduler_id"), int(course_instance_2.scheduler_id))
        self.assertEqual(self.account.choices.count(), 2)

    def test_choice_not_auth(self):
        self.client.logout()
        data = {"scheduler_id": uuid.uuid4()}
        response = self.client.post(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 401)

    def test_choice_wrong_id(self):
        data = {"scheduler_id": uuid.uuid4()}
        response = self.client.post(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 406)

    def test_choice_bad_id(self):
        pass

class TestDeleters(TestCase):
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
        profile_data = [("profile_1", "AAAA", "6CMJU"), 
                        ("profile_2", "BBBB", "6CMJU"), 
                        ("profile_3", "CCCC", "6CDDD")]

        # programs = register_programs(program_data)
        prog_1 = Program.objects.create(program_name="mjukvaruteknik", program_code="6CMJU")
        prog_2 = Program.objects.create(program_name="datateknik", program_code="6CDDD")
        
        profile_1 = Profile.objects.create(profile_name="profile_1", profile_code="AAAA")
        profile_2 = Profile.objects.create(profile_name="profile_2", profile_code="BBBB")
        prog_1.profiles.add(profile_1)
        prog_1.profiles.add(profile_2)
        prog_1.save()

        profile_3 = Profile.objects.create(profile_name="profile_3", profile_code="CCCC")
        prog_2.profiles.add(profile_3)
        prog_2.save()
        
        register_courses([{"course_code": "AAAA",
                           "course_name": "test_course_1",
                           "hp": "6",
                           "program_code": "6CMJU",
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
                           "program_code": "6CMJU",
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
                           }])

        account = Account.objects.get(user__username="test_user")
        account.program = prog_1
        
        for course_instance in Scheduler.objects.all():
            account.choices.add(course_instance)

        account.save()
        self.account = account

        self.client.login(username="test_user", password="123")

    def test_choice(self):
        course_instance = Scheduler.objects.get(course__course_code="AAAA")

        data = {"scheduler_id": course_instance.scheduler_id}
        response = self.client.delete(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("scheduler_id"), -1)
        self.assertEqual(self.account.choices.count(), 3)

    def test_choice_linked(self):
        course_instance_1 = Scheduler.objects.get(course__course_code="CCCC", schedule__period="1")
        course_instance_2 = Scheduler.objects.get(course__course_code="CCCC", schedule__period="2")
        
        data = {"scheduler_id": course_instance_2.scheduler_id}
        response = self.client.delete(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("scheduler_id"), int(course_instance_1.scheduler_id))
        self.assertEqual(self.account.choices.count(), 2)

    def test_choices_not_auth(self):
        self.client.logout()
        data = {"scheduler_id": uuid.uuid4()}
        response = self.client.delete(reverse('api-1.0.0:delete_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.account.choices.count(), 4)

    def test_choices_wrong_id(self):
        data = {"scheduler_id": uuid.uuid4()}
        response = self.client.delete(reverse('api-1.0.0:delete_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 406)
        self.assertEqual(self.account.choices.count(), 4)








