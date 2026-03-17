from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to = 'avatars/', default='avatars/default.jpg')
    english_level = models.CharField(max_length = 2,default='A1')

    def __str__(self):
        return self.username
