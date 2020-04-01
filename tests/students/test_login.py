import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestAccountLogin():
    url = '/api/v1/student/login'

    def test_login(self, client, min_user_data, min_user):
        data = {'email': min_user_data['email'],
                'password': min_user_data['password']}

        response = client.post(
            self.url, data=data, content_type='application/json')
        assert response.status_code == 200

    def test_no_account(self, client, min_user_data):
        data = {'email': min_user_data['email'],
                'password': min_user_data['password']}

        response = client.post(
            self.url, data=data, content_type='application/json')
        assert response.status_code == 400

    def test_account_not_confirmed(self, client, min_user_data, min_user):
        min_user.is_confirmed = False
        min_user.save()
        data = {'email': min_user_data['email'],
                'password': min_user_data['password']}

        response = client.post(
            self.url, data=data, content_type='application/json')
        assert response.status_code == 400

    def test_invalid_password(self, client, min_user_data, min_user):
        data = {'email': min_user_data['email'],
                'password': 'wrong'}

        response = client.post(
            self.url, data=data, content_type='application/json')
        assert response.status_code == 400
