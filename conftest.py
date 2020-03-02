import pytest

from students.models import Student


@pytest.fixture()
def new_user_data():
    new_user = {
        'email': 'test@test.com',
        'matric_number': '20001000',
        'first_name': 'HAKS',
        'last_name': 'HAKS',
        'mobile_number': '09012212244',
        'password': 'money'
    }
    return new_user
