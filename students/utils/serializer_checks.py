import re

from django.utils import timezone
from rest_framework import serializers

from students.utils.constants import mobile_numbers
from students.utils.enums import Departments

class StudentChecker:
    @staticmethod
    def check_name(name, name_type):
        if len(name) < 3:
            raise serializers.ValidationError(
                f'{name_type} should have more than two characters'
            )

        pattern = re.match(r"^[a-zA-Z ]+$", name)
        if not pattern:
            raise serializers.ValidationError(
                f'{name_type} can only allow English alphabets'
            )

        return name

    @staticmethod
    def check_email(email):
        pattern = re.match(r'^[^@\s]+@[^@\s]+\.[^@]+$', email)
        if not pattern:
            raise serializers.ValidationError(
                f'Email is invalid'
            )

        return email

    @staticmethod
    def check_matric_number(matric_number):
        pattern = re.match(r"^[0-9]{8}$", matric_number)
        if not pattern:
            raise serializers.ValidationError(
                f'Matric number is invalid'
            )

        current_year = timezone.now().year
        x_years_back = current_year - 9
        if x_years_back > int(matric_number[:4]) or \
                int(matric_number[:4]) > current_year:
            raise serializers.ValidationError(
                f'Matric number is invalid'
            )

        return matric_number

    @staticmethod
    def check_mobile_number(mobile_number):
        number_combo = "|".join(mobile_numbers)
        pattern = re.match(r"^{}[0-9]+$".format(number_combo), mobile_number)
        if not pattern:
            raise serializers.ValidationError(
                f'Mobile number is invalid'
            )

        if len(mobile_number) > 11:
            raise serializers.ValidationError(
                f'Mobile number is invalid'
            )

        return mobile_number

    @staticmethod
    def check_clinic_number(clinic_number):
        pattern = re.match(r"^ST[0-9]{6}$", clinic_number)
        if not pattern:
            raise serializers.ValidationError(
                f'Clinic number is invalid'
            )

        return clinic_number

    @staticmethod
    def check_department_number(department):
        departments = [dpt.value for dpt in Departments]
        if department not in departments:
            raise serializers.ValidationError(
                f'Department does not exist'
            )

        return department