from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from students.utils.generate import LENGTH_OF_ID, generate_id
from students.utils.enums import BloodGroups, GenoTypes, StudentLevels, Departments, Colleges


class Student(AbstractBaseUser):
    USERNAME_FIELD = 'matric_number'

    id = models.CharField(max_length=LENGTH_OF_ID, primary_key=True, default=generate_id, editable=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    password = models.CharField(max_length=100, null=False)
    mobile_number = models.CharField(max_length=11, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    matric_number = models.CharField(max_length=8, null=False, blank=False, unique=True)
    clinic_number = models.CharField(max_length=8, null=True, unique=True)
    image = models.URLField(null=True)
    college = models.CharField(max_length=10, choices=[(college, college.value) for college in Colleges],
                               null=True)
    department = models.CharField(max_length=5, choices=[(department, department.value) for department in Departments],
                                  null=True)
    blood_group = models.CharField(max_length=15, choices=[(blood_group, blood_group.value) for blood_group in BloodGroups],
                                   null=True)
    genotype = models.CharField(max_length=2, choices=[(geno_type, geno_type.value) for geno_type in GenoTypes],
                                null=True)
    level = models.CharField(max_length=15,
                             choices=[(student_level, student_level.value) for student_level in StudentLevels],
                             null=True)
    is_confirmed = models.BooleanField(default=False)


class Token(models.Model):
    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True, default=generate_id,
        editable=False
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    is_blacklisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Ping(models.Model):
    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True, default=generate_id,
        editable=False
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    location = models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
