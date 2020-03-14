import json
from unittest.mock import patch

import pytest


@pytest.mark.django_db
class TestAccountConfirmation:
    url = '/api/v1/student/confirm'

    @patch('students.serializer.get_from_redis')
    def test_confirm(self, get_redis, client, min_user):
        min_user.is_confirmed = False
        min_user.save()
        id = min_user.id
        url = f'{self.url}/{id}'
        mock_otp = "mock1"
        data = {"otp": mock_otp}
        get_redis.return_value = mock_otp
        response = client.patch(url, data=data,
                                content_type='application/json')
        assert response.status_code == 200

    def test_no_account(self, client):
        id = 'invalid'
        url = f'{self.url}/{id}'
        response = client.patch(url, format='json')
        assert response.status_code == 400
        assert response.data['error'] == 'Student does not have an account'

    def test_account_confirmed(self, client, min_user):
        id = min_user.id
        url = f'{self.url}/{id}'
        response = client.patch(url, format='json')
        assert response.status_code == 400
        assert response.data['error'] == \
               'Student\'s account is already confirmed'

    @patch('students.serializer.get_from_redis')
    def test_invalid_otp(self, get_redis, client, min_user):
        min_user.is_confirmed = False
        min_user.save()
        id = min_user.id
        url = f'{self.url}/{id}'
        data = {'otp': 'test0'}
        mock_otp = 'mock1'
        get_redis.return_value = mock_otp
        response = client.patch(url, data=data,
                                content_type='application/json')
        assert response.status_code == 400
        assert list(response.data['error'].keys()) == ['otp']

