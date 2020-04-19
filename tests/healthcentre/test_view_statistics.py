import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestViewStatistics():
    url = '/api/v1/healthcentre/statistics'

    def test_view_statistics(self, client, sent_ping, max_user, min_user,
                             hc_worker_auth_header):
        response = client.get(
            self.url, content_type='application/json',
            **hc_worker_auth_header)

        ping_count = len((sent_ping, ))
        student_count = len((max_user, min_user))

        assert response.status_code == 200
        assert response.data['data']['pings'] ==ping_count
        assert response.data['data']['students'] == student_count
        assert response.data['message'] == 'Statistics retrieved.'
