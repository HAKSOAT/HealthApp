import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestAccountRegistration():
    url = '/api/v1/register'

    @patch('students.views.send_mail')
    def test_register(self, mock_send_mail, client, new_user_data):
        mock_send_mail.return_value = True
        response = client.post(self.url, data=new_user_data, format='json')
        assert response.status_code == 200
