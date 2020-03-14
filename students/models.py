from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from students.utils.generate import LENGTH_OF_ID, generate_id
from students.utils.enums import Departments, UserTypes


class Student(AbstractBaseUser):
    USERNAME_FIELD = 'matric_number'

    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True,
        default=generate_id, editable=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    password = models.CharField(max_length=100, null=False)
    mobile_number = models.CharField(
        max_length=11, null=True, unique=True)
    email = models.EmailField(
        max_length=100, null=False, blank=False, unique=True)
    matric_number = models.CharField(
        max_length=8, null=True, unique=True)
    clinic_number = models.CharField(max_length=8, null=True, unique=True)
    image = models.URLField(null=True)
    department = models.CharField(
        max_length=5,
        choices=[(department, department.value) for department in Departments],
        null=True)
    is_confirmed = models.BooleanField(default=False)


class Token(models.Model):
    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True, default=generate_id,
        editable=False
    )
    user_id = models.CharField(max_length=LENGTH_OF_ID, default=generate_id)
    user_table = models.CharField(max_length=20,
                                  choices=[(user_type, user_type.value)
                                           for user_type in UserTypes],
                                  default=UserTypes.student)
    token = models.CharField(max_length=500)
    is_blacklisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Ping(models.Model):

    class Meta:
        ordering = ['is_read', '-created_at']

    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True, default=generate_id,
        editable=False
    )
    is_read = models.BooleanField(default=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    location = models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
