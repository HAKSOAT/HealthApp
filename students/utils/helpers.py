from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from students.models import Student
from students.utils.enums import BloodTypes, GenoTypes, StudentLevels, Departments, Colleges


def get_student_fields(new=None):
    all_fields = [field.name for field in Student._meta.fields]
    if new:
        all_fields.append(new)
    return all_fields

def update_student(student, data):
    errors = {}
    min_name_length = 2
    min_name_error = f'Should be at least {min_name_length} characters'
    if data.get('first_name') and len(data.get('first_name')) < min_name_length:
        errors['first_name'] = [min_name_error]
    if data.get('last_name') and len(data.get('last_name')) < 2:
        errors['last_name'] = [min_name_error]

    password_errors = check_password(student, data.get('password'), data.get('new_password'))
    errors.update(password_errors)

    choice_errors = check_choices(data.get('blood_type'), data.get('genotype'), data.get('level'),
                                  data.get('department'), data.get('college'))
    errors.update(choice_errors)
    notupdatable_errors = check_notupdatable(data.get('email'), data.get('matric_number'),
                                             data.get('mobile_number'))
    errors.update(notupdatable_errors)

    if errors:
        return {'errors': errors}
    else:
        return data


def check_choices(blood_type, genotype, level, department, college):
    blood_types = [bt.value for bt in BloodTypes]
    genotypes = [gt.value for gt in GenoTypes]
    levels = [lev.value for lev in StudentLevels]
    departments = [dpt.value for dpt in Departments]
    colleges = [col.value for col in Colleges]
    errors = {}

    if blood_type and blood_type not in blood_types:
        errors['blood_type'] = ['This value is invalid']
    if genotype and genotype not in genotypes:
        errors['genotype'] = ['This value is invalid']
    if level and level not in levels:
        errors['level'] = ['This value is invalid']
    if department and department not in departments:
        errors['department'] = ['This value is invalid']
    if college and college not in colleges:
        errors['college'] = ['This value is invalid']

    return errors


def check_password(student, old, new):
    errors = {}
    if old and not new:
        errors['new_password'] = ['Ensure this value is provided']
    elif not old and new:
        errors['password'] = ['Ensure this value is provided']
    elif old and new and not student.check_password(old):
        errors['password'] = ['Value is incorrect']
    elif old == new:
        errors['new_password'] = ['Value must be different']
    return errors


def check_notupdatable(email, matric_number, mobile_number):
    errors = {}
    if email:
        errors['email'] = ['This value cannot be updated']
    if matric_number:
        errors['matric_number'] = ['This value cannot be updated']
    if mobile_number:
        errors['mobile_number'] = ['This value cannot be updated']

    return errors