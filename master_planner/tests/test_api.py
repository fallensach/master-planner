from django.urls import reverse
from django.test import TestCase
from planning.models import Scheduler, Schedule, Course, Program, Profile, MainField, Examination, register_courses, register_programs, register_profiles
from accounts.models import User, Account
import json


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
        account = Account.objects.get(user__username="test_user")
        account.program = programs[0]
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
        account = Account.objects.get(user__username="test_user")
        account.save()

        self.client.login(username="test_user", password="123")

    def test_choice(self):
        program_data = [("6CMJU", 'Civilingenjörsprogram i mjukvaruteknik')]
        profile_data = [("profile_1", "AAAA")]
        programs = register_programs(program_data)
        
        profiles = register_profiles(programs[0], profile_data[:2])
        
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
        account = Account.objects.get(user__username="test_user")
        account.program = programs[0]
        account.save()
        course_instance = Scheduler.objects.create(course=Course.objects.get(course_code="AAAA"),
                                                   program=programs[0],
                                                   schedule=Schedule.objects.get(semester=7))
        course_instance.profiles.add(Profile.objects.get(profile_code="AAAA"))
        course_instance.save()
        
        data = {"scheduler_id": course_instance.scheduler_id}
        response = self.client.post(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("scheduler_id"), -1)
        self.assertEqual(account.choices.count(), 1)

    def test_choice_linked(self):
        program_data = [("6CMJU", 'Civilingenjörsprogram i mjukvaruteknik')]
        profile_data = [("profile_1", "AAAA")]
        programs = register_programs(program_data)
        
        profiles = register_profiles(programs[0], profile_data[:2])
        
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
        account = Account.objects.get(user__username="test_user")
        account.program = programs[0]
        account.save()
        course_instance = Scheduler.objects.create(course=Course.objects.get(course_code="AAAA"),
                                                   program=programs[0],
                                                   schedule=Schedule.objects.get(semester=7))
        course_instance.profiles.add(Profile.objects.get(profile_code="AAAA"))
        course_instance.save()
        course_instance2 = Scheduler.objects.create(course=Course.objects.get(course_code="BBBB"),
                                                   program=programs[0],
                                                   schedule=Schedule.objects.get(semester=7),
                                                   linked=course_instance)
        course_instance2.profiles.add(Profile.objects.get(profile_code="AAAA"))
        course_instance2.save()
        
        data = {"scheduler_id": course_instance2.scheduler_id}
        response = self.client.post(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("scheduler_id"), course_instance.scheduler_id)
        self.assertEqual(account.choices.count(), 2)

    def test_choice_not_auth(self):
        self.client.logout()
        data = {"scheduler_id": 1}
        response = self.client.post(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 401)

    def test_choice_wrong_id(self):
        data = {"scheduler_id": 1}
        response = self.client.post(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 406)

class TestDeleters(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username="test_user",  
                                        password="123",
                                        is_superuser=True,
                                        is_staff=True)
        account = Account.objects.create(user=user)
        
    def setUp(self):
        account = Account.objects.get(user__username="test_user")
        account.save()

        self.client.login(username="test_user", password="123")

    def test_choice(self):
        program_data = [("6CMJU", 'Civilingenjörsprogram i mjukvaruteknik')]
        profile_data = [("profile_1", "AAAA")]
        programs = register_programs(program_data)
        
        profiles = register_profiles(programs[0], profile_data[:2])
        
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
        account = Account.objects.get(user__username="test_user")
        account.program = programs[0]
        account.save()
        course_instance = Scheduler.objects.create(course=Course.objects.get(course_code="AAAA"),
                                                   program=programs[0],
                                                   schedule=Schedule.objects.get(semester=7))
        course_instance.profiles.add(Profile.objects.get(profile_code="AAAA"))
        course_instance.save()
        account.choices.add(course_instance)
        account.save()


        data = {"scheduler_id": course_instance.scheduler_id}
        response = self.client.delete(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("scheduler_id"), -1)
        self.assertEqual(account.choices.count(), 0)

    def test_choice_linked(self):
        program_data = [("6CMJU", 'Civilingenjörsprogram i mjukvaruteknik')]
        profile_data = [("profile_1", "AAAA")]
        programs = register_programs(program_data)
        
        profiles = register_profiles(programs[0], profile_data[:2])
        
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
        account = Account.objects.get(user__username="test_user")
        account.program = programs[0]
        account.save()
        course_instance = Scheduler.objects.create(course=Course.objects.get(course_code="AAAA"),
                                                   program=programs[0],
                                                   schedule=Schedule.objects.get(semester=7))
        course_instance.profiles.add(Profile.objects.get(profile_code="AAAA"))
        course_instance.save()
        course_instance2 = Scheduler.objects.create(course=Course.objects.get(course_code="BBBB"),
                                                   program=programs[0],
                                                   schedule=Schedule.objects.get(semester=7),
                                                   linked=course_instance)
        course_instance2.profiles.add(Profile.objects.get(profile_code="AAAA"))
        course_instance2.save()
        account.choices.add(course_instance)
        account.choices.add(course_instance2)
        account.save()
        
        data = {"scheduler_id": course_instance2.scheduler_id}
        response = self.client.delete(reverse('api-1.0.0:post_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("scheduler_id"), course_instance.scheduler_id)
        self.assertEqual(account.choices.count(), 0)

    def test_choices_not_auth(self):
        self.client.logout()
        data = {"scheduler_id": 1}
        response = self.client.delete(reverse('api-1.0.0:delete_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 401)

    def test_choices_wrong_id(self):
        data = {"scheduler_id": 100000000}
        response = self.client.delete(reverse('api-1.0.0:delete_choice'), data=data, content_type='application/json')

        self.assertEqual(response.status_code, 406)








