from unittest.mock import patch

import pytest

from students.models import Student


@pytest.mark.django_db
class TestAccountStudent():
    url = '/api/v1/student/profile'

    def test_view_profile(self, client, auth_header):
        response = client.get(self.url, **auth_header)
        assert response.status_code == 200

    def test_password_not_profile_view(self, client, auth_header):
        response = client.get(self.url, **auth_header)
        assert response.status_code == 200
        assert 'password' not in response.data['data'].keys()

    def test_update(self, client, min_user_data, min_user, auth_header):
        new_name = 'CHANGEDHAKS'
        new_password = 'more_money'
        new_matric_number = '20200000'
        data = {'first_name': new_name,
                'last_name': new_name,
                'matric_number': new_matric_number,
                'password': min_user_data['password'],
                'new_password': new_password}
        response = client.patch(self.url, data=data,
                                content_type='application/json',
                                **auth_header)
        assert response.status_code == 200

        student_id = min_user.id
        student = Student.objects.filter(id=student_id).first()
        assert student.first_name == new_name
        assert student.last_name == new_name
        assert student.matric_number == new_matric_number
        assert student.check_password(new_password)

    def test_update_password_invalid(self, client, min_user, auth_header):
        new_password = 'more_money'
        data = {'password': 'Wrong',
                'new_password': new_password}
        response = client.patch(self.url, data=data,
                                content_type='application/json',
                                **auth_header)
        assert response.status_code == 400
        assert 'password' in response.data['error'].keys()

    def test_update_matric_exist(self, client, min_user,
                                 max_user, auth_header):
        data = {'matric_number': max_user.matric_number}
        response = client.patch(self.url, data=data,
                                content_type='application/json',
                                **auth_header)
        assert response.status_code == 400
        assert 'matric_number' in response.data['error'].keys()

    def test_update_email_exist(self, client, min_user, max_user, auth_header):
        data = {'email': max_user.email}
        response = client.patch(self.url, data=data,
                                content_type='application/json',
                                **auth_header)
        assert response.status_code == 400
        assert 'email' in response.data['error'].keys()

    def test_update_mobile_number_exist(self, client, min_user,
                                        max_user, auth_header):
        data = {'mobile_number': max_user.mobile_number}
        response = client.patch(self.url, data=data,
                                content_type='application/json',
                                **auth_header)
        assert response.status_code == 400
        assert 'mobile_number' in response.data['error'].keys()

    def test_update_clinic_number_exist(self, client, min_user,
                                        max_user, auth_header):
        data = {'clinic_number': max_user.clinic_number}
        response = client.patch(self.url, data=data,
                                content_type='application/json',
                                **auth_header)
        assert response.status_code == 400
        assert 'clinic_number' in response.data['error'].keys()
