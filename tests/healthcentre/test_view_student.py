import pytest

from unittest.mock import patch


@pytest.mark.django_db
class TestViewStudent():
    url = '/api/v1/healthcentre/student'

    def test_view_student(self, client, hc_worker_auth_header, max_user):
        student_id = max_user.id
        response = client.get(
            self.url + f'/{student_id}', content_type='application/json',
            **hc_worker_auth_header)
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully retrieved student\'s profile'

    def test_view_all_students(self, client, hc_worker_auth_header, max_user):
        response = client.get(
            self.url, content_type='application/json',
            **hc_worker_auth_header)
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully retrieved students'

    def test_view_students_search(self, client, hc_worker_auth_header, max_user):
        query = 'HAKS'
        response = client.get(
            self.url + "?query=HAKS", content_type='application/json',
            **hc_worker_auth_header)
        assert response.data['data'][0]['first_name'] == query
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully retrieved students'

    def test_nonexistent_student(self, client, hc_worker_auth_header):
        student_id = 'fake'
        response = client.get(
            self.url + f'/{student_id}', content_type='application/json',
            **hc_worker_auth_header)

        assert response.status_code == 404
        assert response.data['message'] == 'Student account does not exist'
