import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestAccountLogin():
    url = '/api/v1/healthcentre/login'

    def test_login(self, client, hc_worker_data,
                   hc_worker):
        data = {'email': hc_worker_data['username'],
                'password': hc_worker_data['password']}

        response = client.post(
            self.url, data=data, content_type='application/json')
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully logged in'

    def test_no_account(self, client):
        data = {'email': 'username',
                'password': 'password'}

        response = client.post(
            self.url, data=data, content_type='application/json')
        assert response.status_code == 400
        assert response.data['error']['email'][0] == 'Account does not exist'

    def test_invalid_password(self, client, hc_worker_data,
                              hc_worker):
        data = {'email': hc_worker_data['username'],
                'password': 'wrong'}

        response = client.post(
            self.url, data=data, content_type='application/json')
        assert response.status_code == 400
        assert response.data['error']['password'][0] == 'Wrong password'
