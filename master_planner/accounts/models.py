from django.db import models, IntegrityError
from django.contrib.auth.models import User
from planning.models import Program, Profile, Scheduler, Course, MainField

class Requirements(models.Model):
    course_instance = models.ManyToManyField(Scheduler, through="RequiredCourses", blank=True)
    field_hp = models.ManyToManyField(MainField, through="RequiredFields", blank=True)
    profile_hp = models.ManyToManyField(Profile, through="RequiredProfiles", blank=True)
    advanced_hp = models.IntegerField()

class RequiredProfiles(models.Model):
    requirement = models.ForeignKey(Requirements, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    hp = models.IntegerField()

class RequiredFields(models.Model):
    requirement = models.ForeignKey(Requirements, on_delete=models.CASCADE)
    field = models.ForeignKey(MainField, on_delete=models.CASCADE)
    hp = models.IntegerField()

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    choices = models.ManyToManyField(Scheduler, blank=True)
    ex_requirements = models.OneToOneField(Requirements, on_delete=CASCADE, blank=True)

    def __str__(self):
        return str(self.user)

    def level_hp(self, profile: str=None) -> dict[float]:
        result_dict = {}

        for semester in range(7, 10):
            for period in range(1, 3):
                result_dict[semester, period, "a_level"] = 0
                result_dict[semester, period, "g_level"] = 0

            result_dict[semester, "a_level"] = 0
            result_dict[semester, "g_level"] = 0

        result_dict["a_level"] = 0
        result_dict["g_level"] = 0
        
        if not profile:
            choices = self.choices.all()
        else:
            choices = self.choices.filter(profiles=profile)

        for choice in choices:
            schedule = choice.schedule

            level = "a_level" if "A" in choice.course.level else "g_level"
            hp = float(choice.course.hp) if "*" not in choice.course.hp else float(choice.course.hp[:-1])/2

            key = (schedule.semester, schedule.period, level)
            result_dict[key] = result_dict[key] + hp
            
            key = (schedule.semester, level)
            result_dict[key] = result_dict[key] + hp

            key = (level)
            result_dict[key] = result_dict[key] + hp
        
        return result_dict

    def field_hp(self):
        pass

    def profile_hp(self):
        pass

def register_account(username: str, email: str, password: str):
    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        account = Account(user=user)
        account.save()
        return True
    
    except IntegrityError:
        return False
    
