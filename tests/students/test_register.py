import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestAccountRegistration():
    url = '/api/v1/register'

    def test_register(self, client, new_user_data):
        response = client.post(self.url, data=new_user_data, format='json')
        assert response.status_code == 200
