from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    current_streak = models.IntegerField(default=0, verbose_name="Поточний стрік")
    last_activity_date = models.DateField(null=True, blank=True, verbose_name="Остання активність")



    def __str__(self):
        return self.username
