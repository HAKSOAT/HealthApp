import pytest

from students.models import Token
from unittest.mock import patch


@pytest.mark.django_db
class TestAccountLogout():
    url = '/api/v1/logout'

    def test_logout(self, client, auth_header):
        response = client.post(self.url, **auth_header)
        assert response.status_code == 200

        token = auth_header['HTTP_AUTHORIZATION'][7:]
        token = Token.objects.filter(token=token).first()
        assert token.is_blacklisted is True

    @patch('students.views.Token.objects.filter')
    def test_already_logged_out(self, logged_out_mock, client, auth_header):
        logged_out_mock.return_value = Token.objects.none()
        response = client.post(self.url, **auth_header)
        assert response.status_code == 400
        assert response.data['error'] == 'Student is already logged out'
