import pytest

from students.models import Student


@pytest.fixture()
def min_user_data():
    """ Minimum needed data to create a student account """
    new_user = {
        'email': 'test@test.com',
        'first_name': 'HAKS',
        'last_name': 'HAKS',
        'password': 'money'
    }
    return new_user

@pytest.fixture()
def max_user_data():
    """ Maximum possible data for a student account """
    new_user = {
        'email': 'test@test.com',
        'first_name': 'HAKS',
        'last_name': 'HAKS',
        'password': 'money',
        'matric_number': '20151228',
        'clinic_number': 'ST052090',
        'mobile_number': '09022205550',
        'image': 'image.com/profile.jpg'
    }
    return new_user

@pytest.fixture()
def min_user(min_user_data):
    """ A student account that fulfills minimum requirements """
    student = Student(**min_user_data)
    student.set_password(min_user_data['password'])
    student.is_confirmed = True
    student.save()
    return student

@pytest.fixture()
def max_user(max_user_data):
    """ A student account that fills all fields """
    student = Student(**max_user_data)
    student.set_password(max_user_data['password'])
    student.is_confirmed = True
    student.save()
    return student


@pytest.fixture()
def auth_header(client, min_user_data, min_user):
    """ Logs in min student to retrieve authetication token """
    response = client.post('/api/v1/student/login',
                           data={
                               'email': min_user_data['email'],
                               'password': min_user_data['password']
                           })
    token = str(response.data["token"], 'utf-8')
    header = {"HTTP_AUTHORIZATION": 'Bearer ' + token}
    return header


@pytest.fixture()
def auth_header_max_user(client, max_user_data, max_user):
    """ Logs in max student to retrieve authetication token """
    response = client.post('/api/v1/student/login',
                           data={
                               'email': max_user_data['email'],
                               'password': max_user_data['password']
                           })
    token = str(response.data["token"], 'utf-8')
    header = {"HTTP_AUTHORIZATION": 'Bearer ' + token}
    return header

