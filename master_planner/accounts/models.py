from django.db import models, IntegrityError
from django.contrib.auth.models import User, AbstractUser
from planning.models import Program, Scheduler

class Account(AbstractUser):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    choices = models.ManyToManyField(Scheduler, blank=True)

    def __str__(self):
        return str(self.username)

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

    
