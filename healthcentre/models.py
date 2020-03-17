from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from students.utils.generate import LENGTH_OF_ID, generate_id
from healthcentre.utils.enums import Roles


class Worker(AbstractBaseUser):
    USERNAME_FIELD = 'username'

    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True,
        default=generate_id, editable=False)
    username = models.CharField(max_length=8, null=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    password = models.CharField(max_length=100, null=False)
    role = models.CharField(max_length=15, choices=[(role, role.value)
                                                    for role in Roles],
                            default=Roles.worker)


class IoT(models.Model):
    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True,
        default=generate_id, editable=False)
    board_name = models.CharField(max_length=50, default='ESP32')
    api_key = models.CharField(max_length=100, default='key')
