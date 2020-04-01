import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestViewPings():
    url = '/api/v1/healthcentre/ping'

    def test_view_ping(self, client, sent_ping, hc_worker_auth_header):
        ping_id = sent_ping.id
        response = client.get(
            self.url + f'/{ping_id}', content_type='application/json',
            **hc_worker_auth_header)

        sent_ping.refresh_from_db()
        assert response.status_code == 200
        assert sent_ping.is_read is True
        assert isinstance(response.data['data'], dict)
        assert response.data['message'] == 'Successfully retrieved Ping'

    def test_nonexistent_ping(self, client, hc_worker_auth_header):
        ping_id = 'fake'
        response = client.get(
            self.url + f'/{ping_id}', content_type='application/json',
            **hc_worker_auth_header)
        assert response.status_code == 404
        assert response.data['message'] == 'Ping does not exist'

    def test_view_all_pings_from_student(self, client, hc_worker_auth_header, sent_ping, max_user):
        data = {'student': max_user.id}
        response = client.get(
            self.url, data=data, content_type='application/json',
            **hc_worker_auth_header)
        assert response.status_code == 200
        assert len(response.data['data']) == 1


    def test_view_all_pings_from_nonexistent_student(self, client, hc_worker_auth_header):
        data = {'student': 'fake'}
        response = client.get(
            self.url, data=data, content_type='application/json',
            **hc_worker_auth_header)
        assert response.status_code == 200
        assert len(response.data['data']) == 0


    def test_view_all_students_pings(self, client, hc_worker_auth_header, sent_ping, max_user):
        response = client.get(
            self.url, content_type='application/json',
            **hc_worker_auth_header)
        assert response.status_code == 200
        assert len(response.data['data']) == 1
