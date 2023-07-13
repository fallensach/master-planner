from django.test import TestCase
from planning.models import *
from accounts.models import *

# Test all registration functions

# class TestApi(TestCase):
#     
#     def setUp(self):
#         user = User.objects.create_user(username="testUser",  
#                                         password="test",)
#         user.save()
#         account = Account.objects.create(user=user)
#         account.save()
#
#
#     def test_something(self):
#         self.client.login(username="testUser", password="123")
#         self.client.get()
