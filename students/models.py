from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from students.utils.generate import LENGTH_OF_ID, generate_id
from students.utils.enums import BloodTypes, GenoTypes, StudentLevels, Departments, Colleges


class Student(AbstractBaseUser):
    USERNAME_FIELD = 'matric_number'

    id = models.CharField(max_length=LENGTH_OF_ID, primary_key=True, default=generate_id, editable=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    password = models.CharField(max_length=100, null=False)
    mobile_number = models.CharField(max_length=11, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    matric_number = models.CharField(max_length=8, null=False, blank=False, unique=True)
    college = models.CharField(max_length=10, choices=[(college, college.value) for college in Colleges],
                               null=True)
    department = models.CharField(max_length=5, choices=[(department, department.value) for department in Departments],
                                  null=True)
    blood_type = models.CharField(max_length=15, choices=[(blood_type, blood_type.value) for blood_type in BloodTypes],
                                  null=True)
    genotype = models.CharField(max_length=2, choices=[(geno_type, geno_type.value) for geno_type in GenoTypes],
                                null=True)
    level = models.CharField(max_length=15,
                             choices=[(student_level, student_level.value) for student_level in StudentLevels],
                             null=True)
    is_confirmed = models.BooleanField(default=False)


class BlackListedToken(models.Model):
    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True, default=generate_id,
        editable=False
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)