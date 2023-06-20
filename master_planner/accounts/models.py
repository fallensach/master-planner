from django.db import models
from django.contrib.auth.models import User
from planning.models import Program, Schedule

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program_code = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    choices = models.ManyToManyField(Schedule, blank=True)

def register_account(username: str, email: str, password: str):
    user = User.objects.create_user(username=username, password=password, email=email)
    account = Account(user=user)
    
    account.save()
    return account
    