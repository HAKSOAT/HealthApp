import pytest
from mixer.backend.django import mixer

from students.models import Student


@pytest.fixture()
def new_user_data():
    new_user = {
        'email': 'test@test.com',
        'matric_number': '20001000'
    }
    mixed_user_data = mixer.blend(Student, **new_user)
    return mixed_user_data
