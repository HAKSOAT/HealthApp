import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestAccountResetPassword():
    url = '/api/v1/reset-password'

    @patch('students.serializer.get_from_redis')
    def test_reset(self, get_redis, client, max_user):
        mock_otp = "mock1"
        password = 'new_password'
        data = {"otp": mock_otp,
                'email': max_user.email,
                'password': password,
                'password_again': password}
        get_redis.return_value = mock_otp
        response = client.patch(self.url, data=data,
                                content_type='application/json')
        assert response.status_code == 200

    def test_no_account(self, client):
        mock_otp = "mock1"
        password = 'new_password'
        data = {"otp": mock_otp,
                'email': 'test@email.com',
                'password': password,
                'password_again': password}
        response = client.patch(self.url, data=data,
                                content_type='application/json')
        assert response.status_code == 400
        assert list(response.data['error'].keys()) == ['email']

    @patch('students.serializer.get_from_redis')
    def test_invalid_otp(self, get_redis, client, max_user):
        mock_otp = "mock1"
        password = 'new_password'
        data = {"otp": 'wrong',
                'email': max_user.email,
                'password': password,
                'password_again': password}
        get_redis.return_value = mock_otp
        response = client.patch(self.url, data=data,
                                content_type='application/json')
        assert response.status_code == 400
        assert list(response.data['error'].keys()) == ['otp']

    @patch('students.serializer.get_from_redis')
    def test_invalid_password(self, get_redis, client, max_user):
        mock_otp = "mock1"
        password = 'new_password'
        data = {"otp": mock_otp,
                'email': max_user.email,
                'password': password,
                'password_again': 'diff_password'}
        get_redis.return_value = mock_otp
        response = client.patch(self.url, data=data,
                                content_type='application/json')
        assert response.status_code == 400
        assert list(response.data['error'].keys()) == ['password']
