import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestAccountPing():
    url = '/api/v1/student/ping'

    def test_ping(self, client, max_user, auth_header_max_user):
        data = {'message': 'testing if i can complain',
                'location': 'test'}
        response = client.post(self.url, data=data,
                               content_type='application/json',
                               **auth_header_max_user)
        assert response.status_code == 201

    def test_incomplete_profile(self, client, min_user, auth_header):
        data = {'message': 'testing if i can complain',
                'location': 'test'}
        response = client.post(self.url, data=data,
                               content_type='application/json',
                               **auth_header)
        assert response.status_code == 400
        assert list(response.data['error'].keys()) == ['matric_number',
                                                       'clinic_number',
                                                       'mobile_number']
