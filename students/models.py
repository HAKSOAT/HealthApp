from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from students.utils.generate import LENGTH_OF_ID, generate_id
from students.utils.enums import Departments, UserTypes
from students.utils.constants import default_student_image


class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_confirmed=True)

    def get_all(self, **filters):
        return super().get_queryset().filter(**filters)


class Student(AbstractBaseUser):
    class Meta:
        ordering = ['-created_at']

    USERNAME_FIELD = 'matric_number'

    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True,
        default=generate_id, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
    image = models.URLField(default=default_student_image)
    department = models.CharField(
        max_length=5,
        choices=[(department, department.value) for department in Departments],
        null=True)
    is_confirmed = models.BooleanField(default=False)
    objects = StudentManager()

    def __repr__(self):
        return f'<{self.email}>'


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
