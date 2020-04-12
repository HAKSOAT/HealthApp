import pytest

from students.models import Student, Ping
from firstaid.models import Tip
from healthcentre.models import Worker


@pytest.fixture()
def min_user_data():
    """ Minimum needed data to create a student account """
    new_user = {
        'email': 'test_min@test.com',
        'first_name': 'HAKS',
        'last_name': 'HAKS',
        'password': 'money'
    }
    return new_user

@pytest.fixture()
def max_user_data():
    """ Maximum possible data for a student account """
    new_user = {
        'email': 'test_max@test.com',
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
    """ Logs in max student to retrieve authentication token """
    response = client.post('/api/v1/student/login',
                           data={
                               'email': max_user_data['email'],
                               'password': max_user_data['password']
                           })
    token = str(response.data["token"], 'utf-8')
    header = {"HTTP_AUTHORIZATION": 'Bearer ' + token}
    return header


@pytest.fixture()
def first_aid_fume_tip():
    """ First aid tip """
    tip = Tip(**{
        "ailment": "Fume inhalation",
        "symptoms": "Headache, confusion, aggression, nausea and vomiting.",
        "causes": "Smoke, Carbon Monoxide.",
        "dos": "Leave area, put off source of fume.",
        "donts": "Don't go into area with strong fume without protection."
    })
    tip.save()
    return tip


@pytest.fixture()
def first_aid_hypnoxia_tip():
    """ First aid tip """
    tip = Tip(**{
        "ailment": "Hypoxia",
        "symptoms": "Rapid breathing, difficulty speaking, headache, grey-blue skin.",
        "causes": "Insufficient oxygen in the body tissue, choking, airway obstruction.",
        "dos": "Take steps to improve breathing such as coughing, do back blows if you know how to.",
        "donts": "Avoid crowded areas, remove breathing obstacles."
    })
    tip.save()
    return tip


@pytest.fixture()
def hc_worker_data():
    """ User data for Health centre worker """
    data = {
        "first_name": "Admin",
        "username": "adad4877",
        "last_name": "Admin",
        "password": "adminuser"
    }
    return data


@pytest.fixture()
def hc_worker(hc_worker_data):
    """ Health centre worker account """
    worker = Worker(**hc_worker_data)
    worker.save()
    worker.set_password(hc_worker_data['password'])
    worker.save()
    return worker



@pytest.fixture()
def hc_worker_auth_header(client, hc_worker_data, hc_worker):
    """ Logs in Healthcentre worker to retrieve authetication token """
    response = client.post('/api/v1/healthcentre/login',
                           data={
                               'email': hc_worker_data['username'],
                               'password': hc_worker_data['password']
                           })
    token = str(response.data["token"], 'utf-8')
    header = {"HTTP_AUTHORIZATION": 'Bearer ' + token}
    return header


@pytest.fixture()
def sent_ping(hc_worker, max_user):
    """ Ping sent by a student """
    ping = Ping(**{
        'student': max_user,
        'message': 'test message to healthcentre',
        'location': 'location'
    })
    ping.save()
    return ping
