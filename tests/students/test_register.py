import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestAccountRegistration():
    url = '/api/v1/student/register'

    @patch('students.views.send_mail')
    def test_register(self, mock_send_mail, client, min_user_data):
        mock_send_mail.return_value = True
        response = client.post(
            self.url, data=min_user_data, format='json')
        assert response.status_code == 200

    def test_existing(self, client, min_user_data, min_user):
        response = client.post(
            self.url, data=min_user_data, format='json')
        assert response.status_code == 400
        assert list(response.data['error'].keys()) == ['email']

    def test_invalid_params(self, client, min_user_data, min_user):
        invalid_data = min_user_data.copy()
        invalid_data['first_name'] = 'A'
        invalid_data['email'] = 'Email'

        response = client.post(self.url, data=invalid_data, format='json')
        assert response.status_code == 400
        assert list(response.data['error'].keys()) == ['first_name', 'email']
