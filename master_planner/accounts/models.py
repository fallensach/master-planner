from django.db import models, IntegrityError
from django.contrib.auth.models import User
from planning.models import Program, Scheduler

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, blank=True, null=True)
    choices = models.ManyToManyField(Scheduler, blank=True)

    def __str__(self):
        return str(self.user)

    @property
    def level_hp(self):
        result_dict = {}

        for semester in range(7, 10):
            for period in range(1, 3):
                result_dict[semester, period, "a_level"] = 0
                result_dict[semester, period, "g_level"] = 0

            result_dict[semester, "a_level"] = 0
            result_dict[semester, "g_level"] = 0

        result_dict["a_level"] = 0
        result_dict["g_level"] = 0
        print(result_dict)
        for choice in self.choices.all():
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

    @property
    def field_hp(self):
        pass

    @property
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
    
def get_user(username: str) -> Account | None:
    """Retrieves user object from Account based on session.

    Args:
        request (_type_): _description_

    Returns:
        Account | None: Account object or None
    """
    try:
        user = User.objects.get(username=username)
        #account = Account.objects.get(user=user)
        return user
    
    except IntegrityError:
        return None
